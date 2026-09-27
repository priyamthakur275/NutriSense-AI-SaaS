"""Prompt templates for the food-detection vision pipeline. Kept as plain
functions returning strings (not a templating engine) — these prompts are
short and don't need Jinja-style control flow; a function is easier to
read, diff, and unit test than a templated file.
"""

from app.schemas.ai_vision import FOOD_CATEGORIES

FOOD_DETECTION_SYSTEM_INSTRUCTION = (
    "You are a food recognition system for an institutional nutrition-monitoring "
    "platform. You analyze photographs of meal trays and identify every distinct "
    "food item present. You respond ONLY with valid JSON matching the exact schema "
    "requested — no markdown formatting, no explanation, no additional commentary."
)


def build_food_detection_prompt() -> str:
    categories = ", ".join(FOOD_CATEGORIES)
    return (
        "Analyze this meal tray photograph and identify every distinct food item visible.\n\n"
        "For each item, estimate:\n"
        "- name: a specific, descriptive name (e.g. 'steamed white rice', not just 'rice')\n"
        f"- category: exactly one of [{categories}]\n"
        "- estimated_portion_grams: your best estimate of the serving size in grams, "
        "based on typical plate/bowl proportions visible in the image\n"
        "- confidence: your confidence in this specific detection, from 0.0 to 1.0\n\n"
        "Respond with ONLY this exact JSON structure, no other text:\n"
        "{\n"
        '  "items": [\n'
        '    {"name": "...", "category": "...", "estimated_portion_grams": 0, "confidence": 0.0}\n'
        "  ],\n"
        '  "overall_confidence": 0.0\n'
        "}\n\n"
        "If you cannot identify any food in the image, return an empty items array "
        "with overall_confidence of 0.0. Do not guess or hallucinate food items that "
        "are not actually visible."
    )
