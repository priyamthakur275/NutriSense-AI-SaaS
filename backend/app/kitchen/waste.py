"""Food-waste analytics over logged kitchen services.

For each dish in each service the kitchen records three weights:
    prepared_kg       what was cooked
    pot_leftover_kg   cooked but never served       -> over-production
    plate_waste_kg    served but left on plates     -> not eaten

From these: served = prepared - pot, eaten = served - plate. Everything on
the waste dashboard (₹ lost, portions lost, nutrients students never
actually ate) is arithmetic on those numbers plus the dish catalogue.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.kitchen.catalog import CATALOG, NUTRIENTS
from app.models.kitchen import KitchenService


def services_in_window(db: Session, owner_id: str, start: date, end: date) -> list[KitchenService]:
    stmt = (
        select(KitchenService)
        .where(
            KitchenService.owner_id == owner_id,
            KitchenService.service_date >= start,
            KitchenService.service_date <= end,
        )
        .order_by(KitchenService.service_date, KitchenService.meal_type)
    )
    return list(db.scalars(stmt))


def _r(x: float, n: int = 1) -> float:
    return round(float(x), n)


def summarize(services: list[KitchenService], days: int) -> dict:
    if not services:
        return {"has_data": False, "days": days}

    tot = defaultdict(float)
    by_dish: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    by_week: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    by_meal: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    week_days: dict[str, set] = defaultdict(set)
    served_nut = defaultdict(float)
    eaten_nut = defaultdict(float)
    plates = 0

    for s in services:
        plates += s.plates_served
        wk = s.service_date - timedelta(days=s.service_date.weekday())
        by_week[wk.isoformat()]["plates"] += s.plates_served
        week_days[wk.isoformat()].add(s.service_date)
        by_meal[s.meal_type.value]["plates"] += s.plates_served
        for d in s.dishes:
            dish = CATALOG.get(d.dish_key)
            cost = dish.cost_per_kg if dish else 0.0
            pot = min(d.pot_leftover_kg, d.prepared_kg)
            served = d.prepared_kg - pot
            plate = min(d.plate_waste_kg, served)
            eaten = served - plate
            waste = pot + plate
            for bucket in (tot, by_dish[d.dish_key], by_week[wk.isoformat()], by_meal[s.meal_type.value]):
                bucket["prepared"] += d.prepared_kg
                bucket["pot"] += pot
                bucket["plate"] += plate
                bucket["eaten"] += eaten
                bucket["cost_wasted"] += waste * cost
            by_dish[d.dish_key]["services"] += 1
            if dish:
                by_dish[d.dish_key]["portions_wasted"] += waste * 1000 / dish.portion_g
                tot["portions_wasted"] += waste * 1000 / dish.portion_g
                for n in NUTRIENTS:
                    served_nut[n] += served * 10 * getattr(dish, n)  # kg -> per-100g units
                    eaten_nut[n] += eaten * 10 * getattr(dish, n)

    def pct(part: float, whole: float) -> float:
        return _r(100 * part / whole) if whole else 0.0

    dishes = []
    for key, b in by_dish.items():
        dish = CATALOG.get(key)
        served = b["prepared"] - b["pot"]
        dishes.append({
            "key": key,
            "name": dish.name if dish else key,
            "services": int(b["services"]),
            "prepared_kg": _r(b["prepared"]),
            "pot_leftover_kg": _r(b["pot"]),
            "plate_waste_kg": _r(b["plate"]),
            "waste_pct": pct(b["pot"] + b["plate"], b["prepared"]),
            "plate_waste_pct": pct(b["plate"], served),
            "cost_wasted": _r(b["cost_wasted"], 0),
            "portions_wasted": int(round(b["portions_wasted"])),
        })
    dishes.sort(key=lambda x: x["cost_wasted"], reverse=True)

    # Weeks at the edge of the window are partial, so the chart uses
    # per-day averages to keep bars comparable.
    weeks = []
    for wk, b in sorted(by_week.items()):
        n_days = len(week_days[wk]) or 1
        weeks.append({
            "week_start": wk,
            "days_logged": n_days,
            "waste_pct": pct(b["pot"] + b["plate"], b["prepared"]),
            "waste_kg": _r(b["pot"] + b["plate"]),
            "pot_kg_per_day": _r(b["pot"] / n_days),
            "plate_kg_per_day": _r(b["plate"] / n_days),
            "cost_wasted": _r(b["cost_wasted"], 0),
        })
    meals = {
        m: {
            "plates": int(b["plates"]),
            "waste_pct": pct(b["pot"] + b["plate"], b["prepared"]),
            "cost_wasted": _r(b["cost_wasted"], 0),
        }
        for m, b in by_meal.items()
    }
    nutrition = [
        {
            "nutrient": n,
            "served_per_plate": _r(served_nut[n] / plates, 1),
            "eaten_per_plate": _r(eaten_nut[n] / plates, 1),
            "lost_pct": pct(served_nut[n] - eaten_nut[n], served_nut[n]),
        }
        for n in NUTRIENTS
    ]

    waste_kg = tot["pot"] + tot["plate"]
    period_days = max(1, (services[-1].service_date - services[0].service_date).days + 1)
    monthly_cost = tot["cost_wasted"] / period_days * 30

    insights = []
    if dishes:
        top = dishes[0]
        insights.append(
            f"{top['name']} wastes the most money: ₹{top['cost_wasted']:,.0f} over this period, "
            f"{top['waste_pct']:g}% of what was cooked."
        )
    if tot["pot"] > tot["plate"]:
        insights.append(
            f"Most waste is over-production ({pct(tot['pot'], waste_kg):g}% never left the pot). "
            "Cooking to the forecast, not to habit, is the biggest lever."
        )
    else:
        insights.append(
            f"Most waste is on plates ({pct(tot['plate'], waste_kg):g}% was served but not eaten). "
            "Smaller first servings or recipe changes help more than cooking less."
        )
    worst_plate = max(dishes, key=lambda x: x["plate_waste_pct"])
    insights.append(
        f"Students leave {worst_plate['plate_waste_pct']:g}% of {worst_plate['name']} on the plate, "
        "the highest of any dish: worth asking why."
    )
    iron = next(x for x in nutrition if x["nutrient"] == "iron_mg")
    insights.append(
        f"Plates were served {iron['served_per_plate']:g} mg of iron on average, but students ate "
        f"{iron['eaten_per_plate']:g} mg. Waste is also a nutrition gap."
    )

    return {
        "has_data": True,
        "days": days,
        "is_sample": all(s.is_sample for s in services),
        "services": len(services),
        "plates": plates,
        "totals": {
            "prepared_kg": _r(tot["prepared"]),
            "eaten_kg": _r(tot["eaten"]),
            "pot_leftover_kg": _r(tot["pot"]),
            "plate_waste_kg": _r(tot["plate"]),
            "waste_kg": _r(waste_kg),
            "waste_pct": pct(waste_kg, tot["prepared"]),
            "cost_wasted": _r(tot["cost_wasted"], 0),
            "portions_wasted": int(round(tot["portions_wasted"])),
            "waste_g_per_plate": _r(waste_kg * 1000 / plates, 0) if plates else 0,
            "monthly_cost_projection": _r(monthly_cost, 0),
        },
        "dishes": dishes,
        "weeks": weeks,
        "meals": meals,
        "nutrition": nutrition,
        "insights": insights,
    }
