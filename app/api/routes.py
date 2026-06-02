from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import Settings, get_settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    RecommendationRequest,
    RecommendationResponse,
    RecommendationResult,
)
from app.services.ollama_client import OllamaClient
from app.services.recommender import FoodRecommender

router = APIRouter()


def get_recommender(request: Request) -> FoodRecommender:
    return request.app.state.recommender


def get_ollama(request: Request) -> OllamaClient:
    return request.app.state.ollama


@router.get("/health", response_model=HealthResponse)
async def health(
    settings: Settings = Depends(get_settings),
    recommender: FoodRecommender = Depends(get_recommender),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        ollama_chat_model=settings.ollama_chat_model,
        ollama_embedding_model=settings.ollama_embedding_model,
        indexed_foods=len(recommender),
    )


@router.post("/recommendations", response_model=RecommendationResponse)
async def recommendations(
    payload: RecommendationRequest,
    recommender: FoodRecommender = Depends(get_recommender),
) -> RecommendationResponse:
    results = await recommender.recommend(payload)
    return RecommendationResponse(query=payload.query, count=len(results), results=results)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    recommender: FoodRecommender = Depends(get_recommender),
    ollama: OllamaClient = Depends(get_ollama),
) -> ChatResponse:
    sources = await recommender.recommend(payload)
    if not sources:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching foods were found for that request.",
        )

    answer = await ollama.chat(settings.ollama_chat_model, _build_messages(payload.query, sources))
    return ChatResponse(
        query=payload.query,
        model=settings.ollama_chat_model,
        answer=answer,
        sources=sources if payload.include_sources else [],
    )


def _build_messages(query: str, sources: list[RecommendationResult]) -> list[dict[str, str]]:
    context = "\n\n".join(
        (
            f"Food: {item.food_name}\n"
            f"Cuisine: {item.cuisine_type}\n"
            f"Calories: {item.food_calories_per_serving}\n"
            f"Ingredients: {', '.join(item.food_ingredients)}\n"
            f"Benefits: {item.food_health_benefits}\n"
            f"Taste: {item.taste_profile}"
        )
        for item in sources
    )

    return [
        {
            "role": "system",
            "content": (
                "You are a practical food recommendation assistant. "
                "Use only the provided food context. Give concise recommendations, "
                "mention why each option fits, and include any relevant calorie notes."
            ),
        },
        {
            "role": "user",
            "content": f"User request: {query}\n\nCandidate foods:\n{context}",
        },
    ]
