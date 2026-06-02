import json
from pathlib import Path
from typing import Any

from app.models.schemas import FoodItem


REQUIRED_DEFAULTS: dict[str, Any] = {
    "food_name": "Unknown",
    "food_description": "",
    "food_calories_per_serving": 0,
    "food_nutritional_factors": {},
    "food_ingredients": [],
    "food_health_benefits": "",
    "cooking_method": "Unknown",
    "cuisine_type": "Unknown",
    "food_features": {},
}


def load_food_data(path: Path) -> list[FoodItem]:
    with path.open("r", encoding="utf-8") as file:
        raw_items = json.load(file)

    seen_ids: dict[str, int] = {}
    foods: list[FoodItem] = []

    for index, raw_item in enumerate(raw_items, start=1):
        item = {**REQUIRED_DEFAULTS, **raw_item}
        base_id = str(item.get("food_id") or index)
        seen_ids[base_id] = seen_ids.get(base_id, 0) + 1
        item["food_id"] = base_id if seen_ids[base_id] == 1 else f"{base_id}_{seen_ids[base_id]}"

        features = item.get("food_features") if isinstance(item.get("food_features"), dict) else {}
        item["food_features"] = features
        item["taste_profile"] = ", ".join(str(value) for value in features.values() if value)
        item["food_ingredients"] = [str(ingredient) for ingredient in item.get("food_ingredients", [])]
        item["food_calories_per_serving"] = int(item.get("food_calories_per_serving") or 0)

        foods.append(FoodItem.model_validate(item))

    return foods


def food_to_document(food: FoodItem) -> str:
    ingredients = ", ".join(food.food_ingredients)
    nutrition = ", ".join(f"{key}: {value}" for key, value in food.food_nutritional_factors.items())
    return (
        f"{food.food_name}. {food.food_description} "
        f"Cuisine: {food.cuisine_type}. Cooking method: {food.cooking_method}. "
        f"Calories per serving: {food.food_calories_per_serving}. "
        f"Ingredients: {ingredients}. Nutrition: {nutrition}. "
        f"Health benefits: {food.food_health_benefits}. "
        f"Taste profile: {food.taste_profile}."
    )
