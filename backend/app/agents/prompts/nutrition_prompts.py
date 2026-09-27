"""Prompt templates for nutrient estimation from a list of detected foods."""

NUTRITION_SYSTEM_INSTRUCTION = (
    "You are a nutrition estimation system. Given a list of food items with "
    "estimated portion sizes, you provide detailed nutrient breakdowns based on "
    "standard nutritional databases (USDA FoodData Central and equivalent "
    "international sources). You respond ONLY with valid JSON matching the exact "
    "schema requested — no markdown formatting, no explanation."
)


def build_nutrition_estimation_prompt(food_items: list[dict]) -> str:
    items_description = "\n".join(
        f"- {item['name']} ({item['category']}), approximately {item['estimated_portion_grams']}g"
        for item in food_items
    )
    return (
        "Estimate the nutritional content of the following food items, each at the "
        "portion size given:\n\n"
        f"{items_description}\n\n"
        "For each item, provide: calories (kcal), protein (g), carbohydrates (g), "
        "fat (g), fiber (g), sugar (g), sodium (mg), and notable vitamins/minerals "
        "(as a dict of nutrient_name -> amount, e.g. vitamin_c_mg, iron_mg, calcium_mg — "
        "include only nutrients present in meaningful amounts for that food).\n\n"
        "Respond with ONLY this exact JSON structure, no other text:\n"
        "{\n"
        '  "items": [\n'
        "    {\n"
        '      "food_name": "...",\n'
        '      "portion_grams": 0,\n'
        '      "nutrients": {\n'
        '        "calories_kcal": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0,\n'
        '        "fiber_g": 0, "sugar_g": 0, "sodium_mg": 0,\n'
        '        "vitamins": {}, "minerals": {}\n'
        "      },\n"
        '      "confidence": 0.0\n'
        "    }\n"
        "  ]\n"
        "}"
    )
