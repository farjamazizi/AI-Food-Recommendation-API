# Food Recommendation System

Production-style FastAPI service for semantic food recommendations.

The API uses:

- FastAPI for HTTP endpoints and OpenAPI docs
- ChromaDB for persistent vector search
- Ollama for local AI models
- `nomic-embed-text` for embeddings
- `llama3.2` for conversational food recommendations

IBM WatsonX is not required.

## Project Paths

- Project: `/home/farjam/food_recommendation_system`
- Conda environment: `/home/farjam/miniconda3/envs/food_recommendation_system`
- Python: `/home/farjam/miniconda3/envs/food_recommendation_system/bin/python3`

## Dataset

The dataset is already stored at `data/FoodDataSet.json`.

Original download command:

```bash
wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/sN1PIR8qp1SJ6K7syv72qQ/FoodDataSet.json -O data/FoodDataSet.json
```

## Local Models

The service is configured for your available Ollama models:

- Chat model: `llama3.2`
- Embedding model: `nomic-embed-text`

Make sure Ollama is running before starting the API:

```bash
ollama list
```

## Install

```bash
cd /home/farjam/food_recommendation_system
/home/farjam/miniconda3/envs/food_recommendation_system/bin/python3 -m pip install -r requirements.txt
```

## Run

```bash
cd /home/farjam/food_recommendation_system
/home/farjam/miniconda3/envs/food_recommendation_system/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

On first startup, the app builds a persistent Chroma index in `.chroma/`.

Open the API docs:

```text
http://localhost:8000/docs
```

## Docker

The Docker image expects Ollama to be reachable from inside the container.

```bash
docker build -t food-recommendation-api .
docker run --rm -p 8000:8000 \
  -e FOOD_API_OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  food-recommendation-api
```

On Linux, you may need to add:

```bash
--add-host=host.docker.internal:host-gateway
```

## Endpoints

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

Semantic recommendations:

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "query": "spicy high protein Indian food",
    "cuisine": "Indian",
    "max_calories": 650,
    "n_results": 5
  }'
```

Conversational recommendation:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want a spicy dinner with rice and good protein",
    "n_results": 4
  }'
```

## Configuration

Copy `.env.example` to `.env` to override settings.

All settings use the `FOOD_API_` prefix, for example:

```bash
FOOD_API_OLLAMA_CHAT_MODEL=granite4
FOOD_API_OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

## Tests

```bash
cd /home/farjam/food_recommendation_system
/home/farjam/miniconda3/envs/food_recommendation_system/bin/python3 -m pytest
```
# AI-Food-Recommendation-API
