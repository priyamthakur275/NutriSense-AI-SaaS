"""Generates eight weeks of realistic sample kitchen logs so a new account
can explore the waste dashboard and the forecast straight away.

The data is synthetic and every row is flagged `is_sample=True`; the UI
labels it as sample data and offers a one-click "clear sample data".

Patterns built in (so the analytics have something real to find):
  - weekends are quieter (Sat ~86%, Sun ~72% of a weekday)
  - attendance drifts up slowly over the period
  - the kitchen habitually cooks ~12% more than the usual headcount
  - some dishes are disliked and come back on plates (lauki, cabbage, salad)
"""

from __future__ import annotations

import hashlib
import random
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.kitchen.catalog import CATALOG
from app.models.enums import MealType
from app.models.kitchen import KitchenService, KitchenServiceDish

WEEKDAY_FACTOR = [1.0, 1.02, 0.99, 1.01, 0.96, 0.86, 0.72]
BASE_HEADCOUNT = {MealType.LUNCH: 380, MealType.DINNER: 340}

# Fixed weekly hostel rotation (Mon..Sun).
ROTATION = {
    MealType.LUNCH: [
        ["steamed_rice", "roti", "dal_tadka", "aloo_gobi", "curd"],
        ["jeera_rice", "roti", "rajma", "cabbage_poriyal", "cucumber_salad"],
        ["steamed_rice", "roti", "sambar", "beans_poriyal", "buttermilk"],
        ["veg_pulao", "roti", "chana_masala", "lauki_sabzi", "curd"],
        ["steamed_rice", "roti", "masoor_dal", "bhindi_fry", "banana"],
        ["lemon_rice", "roti", "moong_dal", "mixed_veg", "curd"],
        ["veg_pulao", "roti", "chana_masala", "palak_paneer", "guava"],
    ],
    MealType.DINNER: [
        ["steamed_rice", "roti", "moong_dal", "mixed_veg"],
        ["steamed_rice", "roti", "dal_tadka", "soya_curry"],
        ["steamed_rice", "roti", "masoor_dal", "aloo_gobi"],
        ["steamed_rice", "roti", "sambar", "cabbage_poriyal"],
        ["steamed_rice", "roti", "dal_tadka", "methi_aloo"],
        ["steamed_rice", "roti", "rajma", "lauki_sabzi"],
        ["jeera_rice", "roti", "moong_dal", "beans_poriyal"],
    ],
}

# Share of a served portion students leave on the plate.
PLATE_WASTE_RATE = {
    "lauki_sabzi": 0.26, "cabbage_poriyal": 0.21, "cucumber_salad": 0.30, "bhindi_fry": 0.15,
    "beans_poriyal": 0.14, "methi_aloo": 0.12, "sambar": 0.12, "steamed_rice": 0.09,
    "jeera_rice": 0.06, "veg_pulao": 0.07, "lemon_rice": 0.08, "roti": 0.05, "dal_tadka": 0.08,
    "moong_dal": 0.10, "masoor_dal": 0.09, "rajma": 0.04, "chana_masala": 0.05,
    "palak_paneer": 0.04, "soya_curry": 0.10, "mixed_veg": 0.11, "aloo_gobi": 0.07,
    "curd": 0.06, "buttermilk": 0.08, "banana": 0.03, "guava": 0.09,
}

# How much of a standard portion students actually take (popular dishes > 1).
TAKE_FACTOR = {"rajma": 1.12, "palak_paneer": 1.1, "chana_masala": 1.08, "lauki_sabzi": 0.82,
               "cabbage_poriyal": 0.88, "cucumber_salad": 0.85, "steamed_rice": 1.05}


def clear_sample(db: Session, owner_id: str) -> int:
    ids = list(db.scalars(select(KitchenService.id).where(
        KitchenService.owner_id == owner_id, KitchenService.is_sample.is_(True)
    )))
    if ids:
        db.execute(delete(KitchenServiceDish).where(KitchenServiceDish.service_id.in_(ids)))
        db.execute(delete(KitchenService).where(KitchenService.id.in_(ids)))
    return len(ids)


def generate_sample(db: Session, owner_id: str, *, today: date | None = None, weeks: int = 8) -> int:
    clear_sample(db, owner_id)
    today = today or date.today()
    seed = int(hashlib.sha256(owner_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    start = today - timedelta(days=weeks * 7)
    created = 0

    for offset in range(weeks * 7):
        day = start + timedelta(days=offset)
        wd = day.weekday()
        for meal_type, base in BASE_HEADCOUNT.items():
            trend = 1 + 0.0012 * offset
            heads = int(round(base * WEEKDAY_FACTOR[wd] * trend * rng.gauss(1, 0.035)))
            # The kitchen cooks for its "usual" number plus a habit buffer.
            usual = base * WEEKDAY_FACTOR[wd] * 1.0
            cook_for = usual * rng.uniform(1.08, 1.16)

            service = KitchenService(
                owner_id=owner_id, service_date=day, meal_type=meal_type,
                plates_served=heads, is_sample=True,
            )
            for key in ROTATION[meal_type][wd]:
                dish = CATALOG[key]
                portion_kg = dish.portion_g / 1000
                prepared = cook_for * portion_kg
                taken = heads * portion_kg * TAKE_FACTOR.get(key, 1.0) * rng.gauss(1, 0.04)
                served = min(prepared, taken)
                pot = max(0.0, prepared - served)
                plate = served * max(0.0, PLATE_WASTE_RATE.get(key, 0.08) * rng.gauss(1, 0.15))
                service.dishes.append(KitchenServiceDish(
                    dish_key=key,
                    prepared_kg=round(prepared, 2),
                    pot_leftover_kg=round(pot, 2),
                    plate_waste_kg=round(plate, 2),
                ))
            db.add(service)
            created += 1
    return created
