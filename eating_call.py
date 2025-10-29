from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from typing import Any, Dict, Iterable, List, Sequence

import data_call

DAY_ORDER: Sequence[str] = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
MEAL_TYPES: Sequence[str] = ("breakfast", "lunch", "dinner")


RECIPES: Dict[str, List[Dict[str, Any]]] = {
    "breakfast": [
        {
            "name": "Quinoa Berry Breakfast Bowl",
            "ingredients": [
                {"item": "cooked quinoa", "quantity": 180.0, "unit": "g"},
                {"item": "unsweetened almond drink", "quantity": 240.0, "unit": "mL"},
                {"item": "blueberries", "quantity": 150.0, "unit": "g"},
                {"item": "chia seeds", "quantity": 15.0, "unit": "g"},
            ],
            "instructions": "Combine cooked quinoa with almond drink, top with blueberries and chia.",
            "base_calories": 360,
            "servings": 1,
            "suitable_for": {"workout", "rest"},
        },
        {
            "name": "Savory Tofu Veggie Scramble",
            "ingredients": [
                {"item": "firm tofu", "quantity": 150.0, "unit": "g"},
                {"item": "spinach", "quantity": 30.0, "unit": "g"},
                {"item": "bell pepper", "quantity": 75.0, "unit": "g"},
                {"item": "olive oil", "quantity": 15.0, "unit": "mL"},
                {"item": "turmeric", "quantity": 1.0, "unit": "g"},
            ],
            "instructions": "Saute crumbled tofu with vegetables in olive oil, season with turmeric.",
            "base_calories": 320,
            "servings": 1,
            "suitable_for": {"workout"},
        },
        {
            "name": "Apple Cinnamon Chia Pudding",
            "ingredients": [
                {"item": "chia seeds", "quantity": 35.0, "unit": "g"},
                {"item": "diced apple", "quantity": 100.0, "unit": "g"},
                {"item": "unsweetened almond drink", "quantity": 240.0, "unit": "mL"},
                {"item": "cinnamon", "quantity": 2.0, "unit": "g"},
            ],
            "instructions": "Mix chia with almond drink, chill overnight, add apple and cinnamon before serving.",
            "base_calories": 290,
            "servings": 1,
            "suitable_for": {"rest"},
        },
        {
            "name": "Banana Hemp Smoothie",
            "ingredients": [
                {"item": "banana", "quantity": 120.0, "unit": "g"},
                {"item": "hemp seeds", "quantity": 20.0, "unit": "g"},
                {"item": "spinach", "quantity": 30.0, "unit": "g"},
                {"item": "water", "quantity": 300.0, "unit": "mL"},
                {"item": "ice", "quantity": 240.0, "unit": "g"},
            ],
            "instructions": "Blend banana with hemp seeds, spinach, and water until smooth.",
            "base_calories": 310,
            "servings": 1,
            "suitable_for": {"workout"},
        },
    ],
    "lunch": [
        {
            "name": "Lentil Quinoa Salad",
            "ingredients": [
                {"item": "green lentils", "quantity": 150.0, "unit": "g"},
                {"item": "cooked quinoa", "quantity": 150.0, "unit": "g"},
                {"item": "cucumber", "quantity": 120.0, "unit": "g"},
                {"item": "cherry tomatoes", "quantity": 150.0, "unit": "g"},
                {"item": "olive oil", "quantity": 25.0, "unit": "mL"},
                {"item": "lemon juice", "quantity": 30.0, "unit": "mL"},
            ],
            "instructions": "Combine lentils and quinoa with chopped vegetables, dress with olive oil and lemon.",
            "base_calories": 460,
            "servings": 1,
            "suitable_for": {"workout", "rest"},
        },
        {
            "name": "Chickpea Avocado Lettuce Wraps",
            "ingredients": [
                {"item": "chickpeas", "quantity": 170.0, "unit": "g"},
                {"item": "ripe avocado", "quantity": 150.0, "unit": "g"},
                {"item": "romaine lettuce", "quantity": 60.0, "unit": "g"},
                {"item": "lime juice", "quantity": 25.0, "unit": "mL"},
            ],
            "instructions": "Mash chickpeas with avocado and lime, serve in lettuce leaves.",
            "base_calories": 430,
            "servings": 1,
            "suitable_for": {"rest"},
        },
        {
            "name": "Grilled Salmon with Sweet Potato",
            "ingredients": [
                {"item": "salmon fillet", "quantity": 170.0, "unit": "g"},
                {"item": "sweet potato", "quantity": 200.0, "unit": "g"},
                {"item": "olive oil", "quantity": 20.0, "unit": "mL"},
                {"item": "rosemary", "quantity": 2.0, "unit": "g"},
            ],
            "instructions": "Roast sweet potato, grill salmon with olive oil and rosemary.",
            "base_calories": 540,
            "servings": 1,
            "suitable_for": {"workout"},
        },
        {
            "name": "Tofu Veggie Bowl",
            "ingredients": [
                {"item": "firm tofu", "quantity": 180.0, "unit": "g"},
                {"item": "brown rice", "quantity": 200.0, "unit": "g"},
                {"item": "broccoli", "quantity": 100.0, "unit": "g"},
                {"item": "carrots", "quantity": 90.0, "unit": "g"},
                {"item": "tamari sauce", "quantity": 30.0, "unit": "mL"},
                {"item": "sesame oil", "quantity": 15.0, "unit": "mL"},
            ],
            "instructions": "Sear tofu, saute vegetables, serve over brown rice with tamari sauce and sesame oil.",
            "base_calories": 500,
            "servings": 1,
            "suitable_for": {"workout", "rest"},
        },
    ],
    "dinner": [
        {
            "name": "Zoodles with Walnut Pesto",
            "ingredients": [
                {"item": "zucchini noodles", "quantity": 360.0, "unit": "g"},
                {"item": "basil", "quantity": 30.0, "unit": "g"},
                {"item": "walnuts", "quantity": 30.0, "unit": "g"},
                {"item": "olive oil", "quantity": 30.0, "unit": "mL"},
                {"item": "garlic", "quantity": 6.0, "unit": "g"},
                {"item": "lemon juice", "quantity": 25.0, "unit": "mL"},
            ],
            "instructions": "Blend pesto ingredients, toss with lightly sauteed zucchini noodles.",
            "base_calories": 380,
            "servings": 1,
            "suitable_for": {"rest"},
        },
        {
            "name": "Cauliflower Rice Stir-Fry",
            "ingredients": [
                {"item": "cauliflower rice", "quantity": 330.0, "unit": "g"},
                {"item": "edamame", "quantity": 150.0, "unit": "g"},
                {"item": "carrots", "quantity": 100.0, "unit": "g"},
                {"item": "bell pepper", "quantity": 150.0, "unit": "g"},
                {"item": "tamari sauce", "quantity": 30.0, "unit": "mL"},
                {"item": "sesame oil", "quantity": 15.0, "unit": "mL"},
            ],
            "instructions": "Stir-fry cauliflower rice with vegetables, finish with tamari sauce and sesame oil.",
            "base_calories": 420,
            "servings": 1,
            "suitable_for": {"workout", "rest"},
        },
        {
            "name": "Baked Cod with Vegetables",
            "ingredients": [
                {"item": "cod fillet", "quantity": 170.0, "unit": "g"},
                {"item": "asparagus", "quantity": 270.0, "unit": "g"},
                {"item": "olive oil", "quantity": 20.0, "unit": "mL"},
                {"item": "lemon", "quantity": 10.0, "unit": "g"},
            ],
            "instructions": "Bake cod with asparagus, drizzle with olive oil and lemon.",
            "base_calories": 480,
            "servings": 1,
            "suitable_for": {"workout"},
        },
        {
            "name": "Stuffed Bell Peppers",
            "ingredients": [
                {"item": "bell peppers", "quantity": 240.0, "unit": "g"},
                {"item": "black beans", "quantity": 170.0, "unit": "g"},
                {"item": "cooked quinoa", "quantity": 150.0, "unit": "g"},
                {"item": "tomato puree", "quantity": 120.0, "unit": "g"},
                {"item": "cilantro", "quantity": 15.0, "unit": "g"},
            ],
            "instructions": "Fill peppers with cooked quinoa and beans mixed with tomato puree, bake until tender.",
            "base_calories": 440,
            "servings": 1,
            "suitable_for": {"rest"},
        },
    ],
}


def forbidden_terms(user_data: Dict[str, Any]) -> Dict[str, Any]:
    diet = user_data.get("eating_diet", {})
    allergies = {item.lower() for item in diet.get("allergies", [])}
    dislikes = {item.lower() for item in diet.get("dislikes", [])}
    restrictions = set()
    for entry in diet.get("restrictions", []):
        entry_lower = entry.lower()
        if entry_lower.startswith("no "):
            restrictions.add(entry_lower.split("no ", 1)[1])
        else:
            restrictions.add(entry_lower)
    return {
        "avoid": allergies | dislikes | restrictions,
        "likes": [item.lower() for item in diet.get("likes", [])],
    }


def recipe_disallowed(recipe: Dict[str, Any], terms_to_avoid: Iterable[str]) -> bool:
    avoided = set(terms_to_avoid)
    for ingredient in recipe["ingredients"]:
        item_lower = ingredient["item"].lower()
        if any(term in item_lower for term in avoided):
            return True
    return False


def recipe_like_hits(recipe: Dict[str, Any], likes: Sequence[str]) -> List[str]:
    lower_ingredients = [ingredient["item"].lower() for ingredient in recipe["ingredients"]]
    return [like for like in likes if any(like in ingredient for ingredient in lower_ingredients)]


def round_to_five(value: float) -> int:
    rounded = int(round(value / 5.0) * 5)
    if value > 0 and rounded == 0:
        return 5
    return max(rounded, 0)


def parse_birthday(raw: str | None) -> date | None:
    if not raw:
        return None
    try:
        parts = [int(part) for part in raw.split("-")]
        if len(parts) == 3:
            return date(parts[0], parts[1], parts[2])
    except (ValueError, TypeError):
        return None
    return None


def calculate_age(birthday: date | None) -> int | None:
    if not birthday:
        return None
    today = date.today()
    years = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        years -= 1
    return max(years, 0)


def basal_metabolic_rate(user: Dict[str, Any]) -> float:
    weight = float(user.get("weight", 70))  # kilograms
    height = float(user.get("height", 175))  # centimeters
    birthday = parse_birthday(user.get("birthday"))
    age = calculate_age(birthday) or 30
    gender = (user.get("gender") or "male").lower()
    gender_offset = 5 if gender == "male" else -161
    return 10 * weight + 6.25 * height - 5 * age + gender_offset


def activity_multiplier(activity_level: str | None) -> float:
    level = (activity_level or "moderate").lower()
    if "sedentary" in level:
        return 1.2
    if "light" in level:
        return 1.375
    if "moderate" in level:
        return 1.55
    if "active" in level:
        return 1.725
    return 1.55


def daily_calorie_target(user: Dict[str, Any], is_workout_day: bool) -> float:
    maintenance = basal_metabolic_rate(user) * activity_multiplier(user.get("activity_level"))
    goal_text = (user.get("goal") or "").lower()
    adjustment = 0.0
    if "lose" in goal_text:
        adjustment -= 250.0 if not is_workout_day else 150.0
    if "gain" in goal_text:
        adjustment += 200.0 if is_workout_day else 100.0
    if "muscle" in goal_text and is_workout_day:
        adjustment += 120.0
    return max(maintenance + adjustment, 1500.0)


def meal_calorie_targets(total_calories: float, is_workout_day: bool) -> Dict[str, float]:
    if is_workout_day:
        ratios = {"breakfast": 0.3, "lunch": 0.4, "dinner": 0.3}
    else:
        ratios = {"breakfast": 0.3, "lunch": 0.35, "dinner": 0.35}
    return {meal: total_calories * share for meal, share in ratios.items()}


def scale_recipe(recipe: Dict[str, Any], target_calories: float) -> Dict[str, Any]:
    base_calories = float(recipe.get("base_calories", 0)) or 1.0
    scale = target_calories / base_calories
    scale = max(0.6, min(2.0, scale))
    scaled_ingredients = []
    for ingredient in recipe["ingredients"]:
        quantity = float(ingredient.get("quantity", 0)) * scale
        unit = ingredient.get("unit", "")
        rounded_quantity = round_to_five(quantity)
        scaled_ingredients.append(
            {
                "item": ingredient["item"],
                "quantity": rounded_quantity,
                "unit": unit,
            }
        )
    return {
        "portion_scale": round(scale, 2),
        "calories": round(base_calories * scale, 0),
        "ingredients": scaled_ingredients,
    }


def choose_recipe(
    meal_type: str,
    workout_day: bool,
    avoid_terms: Iterable[str],
    likes: Sequence[str],
    like_usage: Counter,
    recipe_usage: Counter,
    max_like_per_item: int,
    max_like_meals: int,
    total_like_meals: int,
) -> Dict[str, Any]:
    candidates = RECIPES.get(meal_type, [])
    allowed_candidates: List[Dict[str, Any]] = []
    for recipe in candidates:
        if workout_day and "workout" not in recipe["suitable_for"]:
            continue
        if not workout_day and "rest" not in recipe["suitable_for"]:
            continue
        if recipe_disallowed(recipe, avoid_terms):
            continue
        likes_in_recipe = recipe_like_hits(recipe, likes)
        if likes_in_recipe:
            if total_like_meals >= max_like_meals:
                continue
            if any(like_usage[like] >= max_like_per_item for like in likes_in_recipe):
                continue
        allowed_candidates.append(recipe)

    if not allowed_candidates:
        # Relax like constraints if no candidate could be found.
        for recipe in candidates:
            if workout_day and "workout" not in recipe["suitable_for"]:
                continue
            if not workout_day and "rest" not in recipe["suitable_for"]:
                continue
            if recipe_disallowed(recipe, avoid_terms):
                continue
            allowed_candidates.append(recipe)

    if not allowed_candidates:
        raise ValueError(f"No suitable recipes available for {meal_type}.")

    allowed_candidates.sort(key=lambda item: recipe_usage[item["name"]])
    chosen = allowed_candidates[0]
    likes_in_recipe = recipe_like_hits(chosen, likes)
    for like in likes_in_recipe:
        like_usage[like] += 1
    if likes_in_recipe:
        like_usage["__total__"] += 1
    recipe_usage[chosen["name"]] += 1
    return chosen


def plan_week(
    user: Dict[str, Any],
    workout_week: Dict[str, Any],
) -> Dict[str, Any]:
    terms = forbidden_terms(user)
    avoid_terms = terms["avoid"]
    likes = terms["likes"]
    like_usage: Counter = Counter()
    recipe_usage: Counter = Counter()
    max_like_per_item = 1
    max_like_meals = max(3, len(likes))

    workout_days = {session["day"] for session in workout_week.get("sessions", [])}
    meals_per_day: List[Dict[str, Any]] = []

    for day in DAY_ORDER:
        is_workout_day = day in workout_days
        daily_target = daily_calorie_target(user, is_workout_day)
        per_meal_targets = meal_calorie_targets(daily_target, is_workout_day)
        total_estimated = 0.0

        day_plan: Dict[str, Any] = {
            "day": day,
            "is_workout_day": is_workout_day,
            "calorie_target": round(daily_target, 0),
            "meals": {},
        }
        for meal_type in MEAL_TYPES:
            recipe = choose_recipe(
                meal_type,
                is_workout_day,
                avoid_terms,
                likes,
                like_usage,
                recipe_usage,
                max_like_per_item,
                max_like_meals,
                like_usage.get("__total__", 0),
            )
            scaled = scale_recipe(recipe, per_meal_targets[meal_type])
            total_estimated += scaled["calories"]
            day_plan["meals"][meal_type] = {
                "name": recipe["name"],
                "instructions": recipe["instructions"],
                "calorie_target": round(per_meal_targets[meal_type], 0),
                "estimated_calories": scaled["calories"],
                "portion_scale": scaled["portion_scale"],
                "ingredients": scaled["ingredients"],
            }

        day_plan["estimated_calories"] = round(total_estimated, 0)
        meals_per_day.append(day_plan)

    return {
        "week": workout_week.get("week"),
        "days": meals_per_day,
    }


def build_meal_plan(weeks: int, uid: str | None = None) -> Dict[str, Any]:
    if weeks <= 0:
        raise ValueError("Weeks must be a positive integer.")

    user_id = uid or data_call.DEFAULT_USER_ID
    user = data_call.get_user_profile(user_id)
    workout_plan = data_call.get_user_workout_plan(user_id)
    plan_weeks = workout_plan.get("weeks", [])
    if not plan_weeks:
        raise ValueError("Workout plan does not contain weekly sessions.")

    planned_weeks: List[Dict[str, Any]] = []
    for index in range(weeks):
        week_data = plan_weeks[index % len(plan_weeks)]
        planned_weeks.append(plan_week(user, week_data))

    return {
        "user_id": user.get("id"),
        "user_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        "weeks": planned_weeks,
    }


def generate_shopping_list(meal_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    quantities: Dict[tuple[str, str], float] = {}
    for week in meal_plan.get("weeks", []):
        for day in week.get("days", []):
            for meal in day.get("meals", {}).values():
                for ingredient in meal.get("ingredients", []):
                    key = (ingredient.get("item"), ingredient.get("unit", ""))
                    if key not in quantities:
                        quantities[key] = 0.0
                    quantities[key] += float(ingredient.get("quantity", 0.0))
    shopping_entries = []
    for (item, unit), total in sorted(quantities.items()):
        rounded_total = round_to_five(total)
        shopping_entries.append(
            {
                "ingredient": item,
                "quantity": rounded_total,
                "unit": unit,
            }
        )
    return shopping_entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate meal suggestions aligned with the workout plan.")
    parser.add_argument("weeks", type=int, nargs="?", default=1, help="Number of weeks to generate (default: 1)")
    parser.add_argument("--shopping-list", action="store_true", help="Include aggregated shopping list in the output")
    parser.add_argument("--uid", default=data_call.DEFAULT_USER_ID, help="User ID to build the meal plan for")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = build_meal_plan(args.weeks, args.uid)
    if args.shopping_list:
        shopping_list = generate_shopping_list(plan)
        output = {"meal_plan": plan, "shopping_list": shopping_list}
    else:
        output = plan
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
