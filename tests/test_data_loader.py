from pathlib import Path

from app.services.data_loader import load_food_data


def test_load_food_data_normalizes_ids_and_required_fields() -> None:
    foods = load_food_data(Path("data/FoodDataSet.json"))

    assert len(foods) == 185
    assert len({food.food_id for food in foods}) == len(foods)
    assert all(isinstance(food.food_id, str) for food in foods)
    assert all(food.food_name for food in foods)
