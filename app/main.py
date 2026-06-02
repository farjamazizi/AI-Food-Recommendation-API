from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings
from app.services.data_loader import load_food_data
from app.services.ollama_client import OllamaClient
from app.services.recommender import FoodRecommender

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    foods = load_food_data(settings.data_path)
    ollama = OllamaClient(settings.ollama_base_url, settings.ollama_timeout_seconds)
    if not await ollama.health():
        raise RuntimeError(f"Ollama is not available at {settings.ollama_base_url}")

    recommender = FoodRecommender(
        foods=foods,
        chroma_path=str(settings.chroma_path),
        collection_name=settings.chroma_collection,
        ollama=ollama,
        embedding_model=settings.ollama_embedding_model,
    )
    logger.info("Building or reusing Chroma index for %s foods", len(foods))
    await recommender.ensure_index()

    app.state.ollama = ollama
    app.state.recommender = recommender
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
