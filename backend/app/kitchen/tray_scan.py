"""Before/after tray photo -> how much of each dish was left uneaten.

The two photos are placed side by side in one image (served on the left,
returned on the right) so any vision model that accepts a single image can
compare them. The model returns JSON; we map its dish names onto the
catalogue and convert "fraction left" into grams using standard portions.
"""

from __future__ import annotations

import io

from PIL import Image, ImageDraw
from pydantic import BaseModel, Field

from app.agents.providers.base import LLMProvider
from app.agents.providers.factory import call_with_failover
from app.agents.utils.json_parsing import parse_structured_response
from app.kitchen.catalog import CATALOG, match_dish

MAX_SIDE = 768

SYSTEM = (
    "You are a food-waste auditor in an Indian institutional canteen. You compare a meal tray "
    "photographed when served (LEFT half of the image) with the same tray when returned (RIGHT half). "
    "Reply with JSON only."
)

PROMPT = (
    "Identify each dish on the served tray (left). For each dish estimate what fraction of the served "
    "amount is still left on the returned tray (right): 0 means fully eaten, 1 means untouched. "
    "Use common Indian dish names (e.g. steamed rice, roti, dal tadka, sambar, rajma, aloo gobi, curd).\n"
    'Return exactly: {"items": [{"dish": "<name>", "leftover_fraction": <0..1>, "confidence": <0..1>}], '
    '"notes": "<one short sentence>"}'
)


class _ScanItem(BaseModel):
    dish: str
    leftover_fraction: float = Field(ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)


class _ScanResult(BaseModel):
    items: list[_ScanItem]
    notes: str | None = None


def _fit(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return img


def stitch(before: bytes, after: bytes) -> bytes:
    """Side-by-side JPEG: served (left) | returned (right), with labels."""
    a, b = _fit(Image.open(io.BytesIO(before))), _fit(Image.open(io.BytesIO(after)))
    h = max(a.height, b.height)
    canvas = Image.new("RGB", (a.width + b.width + 12, h + 28), "white")
    canvas.paste(a, (0, 28))
    canvas.paste(b, (a.width + 12, 28))
    draw = ImageDraw.Draw(canvas)
    draw.text((8, 8), "SERVED", fill="black")
    draw.text((a.width + 20, 8), "RETURNED", fill="black")
    out = io.BytesIO()
    canvas.save(out, "JPEG", quality=88)
    return out.getvalue()


def to_report(result: _ScanResult, provider: str) -> dict:
    items = []
    for it in result.items:
        dish = match_dish(it.dish)
        portion = dish.portion_g if dish else None
        items.append({
            "detected": it.dish,
            "key": dish.key if dish else None,
            "name": dish.name if dish else it.dish.title(),
            "leftover_pct": round(it.leftover_fraction * 100),
            "leftover_g": round(portion * it.leftover_fraction) if portion else None,
            "confidence": round(it.confidence, 2),
        })
    known = [i for i in items if i["leftover_g"] is not None]
    total_served = sum(CATALOG[i["key"]].portion_g for i in known)
    total_left = sum(i["leftover_g"] for i in known)
    return {
        "items": items,
        "plate_leftover_g": total_left,
        "plate_leftover_pct": round(100 * total_left / total_served) if total_served else None,
        "notes": result.notes,
        "provider": provider,
    }


async def scan_trays(before: bytes, after: bytes) -> dict:
    image = stitch(before, after)

    async def _call(provider: LLMProvider):
        return await provider.generate_from_image(
            PROMPT, image, mime_type="image/jpeg", system_instruction=SYSTEM, temperature=0.1,
        )

    response = await call_with_failover(_call)
    result = parse_structured_response(response.content, _ScanResult)
    return to_report(result, response.provider)
