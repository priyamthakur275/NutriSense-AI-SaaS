"""Food image analysis pipeline and nutrition estimation engine tests."""

import io
import json

import pytest
from PIL import Image

from app.agents.nutrition.nutrition_engine import estimate_nutrition, persist_nutrition_record
from app.agents.providers import factory
from app.agents.providers.base import LLMResponse
from app.agents.vision.food_detection_service import analyze_food_image
from app.core.config import settings
from app.core.exceptions import DuplicateResourceError
from app.core.file_validation import validate_upload_file
from app.schemas.ai_vision import DetectedFoodItem


def _make_test_jpeg() -> bytes:
    img = Image.new("RGB", (800, 600), color=(200, 150, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class _FakeUploadFile:
    filename = "tray.jpg"

    def __init__(self, content: bytes):
        self._content = content

    async def read(self):
        return self._content


class _StubVisionProvider:
    name = "stub-vision"

    async def generate_from_image(self, prompt, image_bytes, **kwargs):
        payload = {
            "items": [
                {"name": "steamed rice", "category": "rice", "estimated_portion_grams": 150, "confidence": 0.92},
                {"name": "grilled chicken breast", "category": "meat", "estimated_portion_grams": 120, "confidence": 0.88},
            ],
            "overall_confidence": 0.9,
        }
        return LLMResponse(content=json.dumps(payload), provider="stub-vision", model="stub")

    async def generate_text(self, prompt, **kwargs):
        payload = {
            "items": [
                {
                    "food_name": "steamed rice", "portion_grams": 150,
                    "nutrients": {"calories_kcal": 195, "protein_g": 4, "carbs_g": 42, "fat_g": 0.4,
                                  "fiber_g": 0.6, "sugar_g": 0.1, "sodium_mg": 2, "vitamins": {}, "minerals": {"iron_mg": 0.2}},
                    "confidence": 0.9,
                },
                {
                    "food_name": "grilled chicken breast", "portion_grams": 120,
                    "nutrients": {"calories_kcal": 198, "protein_g": 37, "carbs_g": 0, "fat_g": 4.3,
                                  "fiber_g": 0, "sugar_g": 0, "sodium_mg": 85, "vitamins": {}, "minerals": {"iron_mg": 1.1}},
                    "confidence": 0.85,
                },
            ]
        }
        return LLMResponse(content=json.dumps(payload), provider="stub-vision", model="stub")


@pytest.fixture(autouse=True)
def _use_stub_vision_provider():
    factory._BUILDERS["stub-vision"] = lambda: _StubVisionProvider()
    settings.AI_PROVIDER = "stub-vision"
    settings.AI_FALLBACK_PROVIDERS = []


@pytest.mark.asyncio
async def test_upload_validation_accepts_real_jpeg():
    content = await validate_upload_file(_FakeUploadFile(_make_test_jpeg()))
    assert len(content) > 0


@pytest.mark.asyncio
async def test_upload_validation_rejects_non_image_content():
    from app.core.exceptions import ValidationAppError

    fake_file = _FakeUploadFile(b"not an image, just plain text pretending to be one")
    with pytest.raises(ValidationAppError):
        await validate_upload_file(fake_file)


@pytest.mark.asyncio
async def test_vision_pipeline_detects_and_preprocesses():
    validated = await validate_upload_file(_FakeUploadFile(_make_test_jpeg()))
    result = await analyze_food_image(validated)

    assert len(result.detected_items) == 2
    assert result.detected_items[0].name == "steamed rice"
    assert result.original_width == 800
    assert result.original_height == 600
    assert result.processed_size_bytes < result.original_width * result.original_height  # was compressed


@pytest.mark.asyncio
async def test_nutrition_totals_are_computed_deterministically_not_from_llm():
    items = [
        DetectedFoodItem(name="steamed rice", category="rice", estimated_portion_grams=150, confidence=0.9),
        DetectedFoodItem(name="grilled chicken breast", category="meat", estimated_portion_grams=120, confidence=0.85),
    ]
    result = await estimate_nutrition(items)

    # 195 + 198 exactly — proves totals are summed in Python, not asked of the LLM
    assert result.totals.calories_kcal == pytest.approx(393.0)
    assert result.totals.protein_g == pytest.approx(41.0)


@pytest.mark.asyncio
async def test_nutrition_record_persists_via_existing_repository(db_session, make_institution, make_meal):
    institution = make_institution()
    meal = make_meal(institution)

    items = [DetectedFoodItem(name="test food", category="other", estimated_portion_grams=100, confidence=0.9)]
    result = await estimate_nutrition(items)
    record = persist_nutrition_record(db_session, meal.id, result)

    assert record.meal_id == meal.id
    assert record.calories_kcal > 0


@pytest.mark.asyncio
async def test_duplicate_nutrition_record_for_same_meal_is_rejected(db_session, make_institution, make_meal):
    institution = make_institution()
    meal = make_meal(institution)
    items = [DetectedFoodItem(name="test food", category="other", estimated_portion_grams=100, confidence=0.9)]
    result = await estimate_nutrition(items)

    persist_nutrition_record(db_session, meal.id, result)
    with pytest.raises(DuplicateResourceError):
        persist_nutrition_record(db_session, meal.id, result)
