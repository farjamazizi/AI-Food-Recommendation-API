from chromadb import PersistentClient

from app.models.schemas import FoodItem, RecommendationRequest, RecommendationResult
from app.services.data_loader import food_to_document
from app.services.ollama_client import OllamaClient


class FoodRecommender:
    def __init__(
        self,
        foods: list[FoodItem],
        chroma_path: str,
        collection_name: str,
        ollama: OllamaClient,
        embedding_model: str,
    ) -> None:
        self.foods = foods
        self.ollama = ollama
        self.embedding_model = embedding_model
        self.client = PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def __len__(self) -> int:
        return len(self.foods)

    async def ensure_index(self) -> None:
        if self.collection.count() == len(self.foods):
            return

        existing = set(self.collection.get(include=[])["ids"])
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, str | int]] = []
        embeddings: list[list[float]] = []

        for food in self.foods:
            if food.food_id in existing:
                continue

            document = food_to_document(food)
            ids.append(food.food_id)
            documents.append(document)
            embeddings.append(await self.ollama.embed(self.embedding_model, document))
            metadatas.append(
                {
                    "name": food.food_name,
                    "description": food.food_description,
                    "cuisine_type": food.cuisine_type,
                    "calories": food.food_calories_per_serving,
                    "ingredients": ", ".join(food.food_ingredients),
                    "health_benefits": food.food_health_benefits,
                    "cooking_method": food.cooking_method,
                    "taste_profile": food.taste_profile,
                }
            )

        if ids:
            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

    async def recommend(self, request: RecommendationRequest) -> list[RecommendationResult]:
        where = self._build_where(request)
        query_embedding = await self.ollama.embed(self.embedding_model, request.query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=request.n_results,
            where=where,
        )

        recommendations: list[RecommendationResult] = []
        ids = results.get("ids", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for food_id, metadata, distance in zip(ids, metadatas, distances, strict=False):
            ingredients = [
                ingredient.strip()
                for ingredient in str(metadata.get("ingredients", "")).split(",")
                if ingredient.strip()
            ]
            recommendations.append(
                RecommendationResult(
                    food_id=food_id,
                    food_name=str(metadata.get("name", "")),
                    food_description=str(metadata.get("description", "")),
                    cuisine_type=str(metadata.get("cuisine_type", "")),
                    food_calories_per_serving=int(metadata.get("calories", 0)),
                    food_ingredients=ingredients,
                    food_health_benefits=str(metadata.get("health_benefits", "")),
                    cooking_method=str(metadata.get("cooking_method", "")),
                    taste_profile=str(metadata.get("taste_profile", "")),
                    similarity_score=max(0.0, 1.0 - float(distance)),
                )
            )

        return self._filter_by_ingredients(recommendations, request.ingredients)

    def _build_where(self, request: RecommendationRequest) -> dict | None:
        filters: list[dict] = []
        if request.cuisine:
            filters.append({"cuisine_type": request.cuisine})
        if request.max_calories is not None:
            filters.append({"calories": {"$lte": request.max_calories}})

        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return {"$and": filters}

    def _filter_by_ingredients(
        self,
        results: list[RecommendationResult],
        required_ingredients: list[str],
    ) -> list[RecommendationResult]:
        if not required_ingredients:
            return results

        required = {ingredient.casefold() for ingredient in required_ingredients}
        filtered: list[RecommendationResult] = []
        for result in results:
            available = {ingredient.casefold() for ingredient in result.food_ingredients}
            if required.issubset(available):
                filtered.append(result)
        return filtered
