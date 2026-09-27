"""Prompt template for personalized recommendation generation. Takes the
user's health profile and their recent nutrition intake summary and asks
for five categories of guidance: meal suggestions, healthier alternatives,
nutrient deficiency alerts, daily advice, and weekly improvement
suggestions — matching the mission's required output categories.

Institution-level dietary policies are NOT currently modeled anywhere in
the schema (no InstitutionPolicy table exists), so they are honestly
omitted from this prompt rather than fabricated — see the recommendation
engine module docstring for the same note.
"""

from app.models.enums import AIRecommendationType

RECOMMENDATION_SYSTEM_INSTRUCTION = (
    "You are a registered-dietitian-level nutrition advisor for an institutional "
    "nutrition platform. You give safe, practical, evidence-based guidance tailored "
    "to the individual's health profile and recent eating patterns. You are "
    "conservative about medical claims — for any flagged medical condition, you "
    "give general dietary guidance only and explicitly recommend consulting a "
    "healthcare professional for anything condition-specific. You respond ONLY "
    "with valid JSON matching the exact schema requested."
)


def build_recommendation_prompt(*, profile_summary: str, nutrition_summary: str) -> str:
    types = ", ".join(t.value for t in AIRecommendationType)
    return (
        f"User health profile:\n{profile_summary}\n\n"
        f"Recent nutrition intake (last 7 days, averaged):\n{nutrition_summary}\n\n"
        "Generate personalized recommendations covering these areas:\n"
        "1. Meal suggestions appropriate for this profile and goal\n"
        "2. Healthier alternatives to any concerning patterns in recent intake\n"
        "3. Nutrient deficiency alerts, if the recent averages suggest a gap\n"
        "4. General daily nutrition advice\n"
        "5. A weekly improvement suggestion\n\n"
        "Produce 3 to 6 total suggestions (not necessarily one per area — skip an "
        "area if there's nothing meaningful to say). For each, set recommendation_type "
        f"to exactly one of: {types}.\n\n"
        "If the profile has any listed medical conditions or food allergies, ensure "
        "every suggestion respects them and never recommends a restricted food.\n\n"
        "Respond with ONLY this exact JSON structure, no other text:\n"
        "{\n"
        '  "suggestions": [\n'
        '    {"recommendation_type": "...", "content": "..."}\n'
        "  ]\n"
        "}"
    )
