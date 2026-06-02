from typing import Any

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    food_id: str
    food_name: str
    food_description: str
    food_calories_per_serving: int
    food_nutritional_factors: dict[str, str]
    food_ingredients: list[str]
    food_health_benefits: str
    cooking_method: str
    cuisine_type: str
    food_features: dict[str, Any]
    taste_profile: str = ""


class RecommendationRequest(BaseModel):
    query: str = Field(min_length=1, examples=["high protein spicy Indian food"])
    cuisine: str | None = Field(default=None, examples=["Indian"])
    max_calories: int | None = Field(default=None, ge=0, examples=[500])
    ingredients: list[str] = Field(default_factory=list, examples=[["chicken", "rice"]])
    n_results: int = Field(default=5, ge=1, le=20)


class RecommendationResult(BaseModel):
    food_id: str
    food_name: str
    food_description: str
    cuisine_type: str
    food_calories_per_serving: int
    food_ingredients: list[str]
    food_health_benefits: str
    cooking_method: str
    taste_profile: str
    similarity_score: float


class RecommendationResponse(BaseModel):
    query: str
    count: int
    results: list[RecommendationResult]


class ChatRequest(RecommendationRequest):
    include_sources: bool = True


class ChatResponse(BaseModel):
    query: str
    model: str
    answer: str
    sources: list[RecommendationResult] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    ollama_chat_model: str
    ollama_embedding_model: str
    indexed_foods: int
