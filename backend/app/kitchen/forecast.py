"""Headcount forecast and cooking quantities.

Plain-English version (what to tell a recruiter):
    "It looks at how many plates were served at the same meal over the last
    eight weeks, learns the weekly pattern (weekends are quieter) and the
    recent trend, and predicts tomorrow's headcount with a range. Then it
    turns that into kilos to cook per dish, using how much students actually
    take of each dish rather than a textbook portion. I measured its accuracy
    by replaying the past: predicting each recent day using only the data
    before it."

Technical version (classical decomposition, no black box):
    weekday factor  f[w] = mean(plates on weekday w) / mean(all plates)
    deseasonalised  s_t  = plates_t / f[weekday(t)]
    level           exponentially weighted mean of s_t (half-life 14 days)
    trend           least-squares slope of s_t over the last 28 days
    forecast        (level + trend · days_ahead) · f[weekday(target)] · event
    range           ± 1.28 σ (80% interval), σ = backtest percentage error
    cook for        the 80th-percentile headcount, so running out is rare
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from app.kitchen.catalog import CATALOG
from app.models.kitchen import KitchenService

EVENTS = {
    "none": (1.0, "Normal day"),
    "exams": (1.05, "Exam week: more students stay in"),
    "long_weekend": (0.7, "Long weekend: many go home"),
    "festival": (0.55, "Festival holiday"),
    "guest_event": (1.2, "Guests or an event on campus"),
}

HALF_LIFE_DAYS = 14
MIN_HISTORY = 7


@dataclass
class _Point:
    day: date
    plates: int


def _weekday_factors(points: list[_Point]) -> list[float]:
    overall = statistics.fmean(p.plates for p in points)
    by_wd: dict[int, list[int]] = defaultdict(list)
    for p in points:
        by_wd[p.day.weekday()].append(p.plates)
    return [statistics.fmean(by_wd[w]) / overall if by_wd.get(w) else 1.0 for w in range(7)]


def _predict(points: list[_Point], target: date) -> float:
    """Point forecast for `target` from `points` (all strictly before it)."""
    f = _weekday_factors(points)
    last = points[-1].day
    num = den = 0.0
    for p in points:
        w = 0.5 ** ((last - p.day).days / HALF_LIFE_DAYS)
        num += w * p.plates / f[p.day.weekday()]
        den += w
    level = num / den

    recent = [p for p in points if (last - p.day).days < 28]
    slope = 0.0
    if len(recent) >= 7:
        xs = [(p.day - last).days for p in recent]
        ys = [p.plates / f[p.day.weekday()] for p in recent]
        mx, my = statistics.fmean(xs), statistics.fmean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx:
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            # The level is a weighted *average*, which lags a trend by about
            # the weighted mean age of the data; add that back too.
            slope = max(min(slope, level * 0.01), -level * 0.01)  # cap ±1%/day
    mean_age = sum(0.5 ** ((last - p.day).days / HALF_LIFE_DAYS) * (last - p.day).days for p in points) / den
    days_ahead = (target - last).days + mean_age
    return max(0.0, (level + slope * days_ahead) * f[target.weekday()])


def _backtest(points: list[_Point], n: int = 28) -> tuple[float | None, float | None, float | None]:
    """Replay the last `n` days: forecast each from only earlier data.
    Returns (MAPE %, σ of % error, naive same-weekday-last-week MAPE %)."""
    errs, naive_errs = [], []
    for i in range(max(MIN_HISTORY, len(points) - n), len(points)):
        actual = points[i].plates
        if actual <= 0:
            continue
        pred = _predict(points[:i], points[i].day)
        errs.append((pred - actual) / actual)
        week_ago = next((p for p in reversed(points[:i]) if (points[i].day - p.day).days == 7), None)
        if week_ago:
            naive_errs.append(abs(week_ago.plates - actual) / actual)
    if not errs:
        return None, None, None
    mape = 100 * statistics.fmean(abs(e) for e in errs)
    sigma = statistics.pstdev(errs) if len(errs) > 1 else abs(errs[0])
    naive = 100 * statistics.fmean(naive_errs) if naive_errs else None
    return round(mape, 1), sigma, (round(naive, 1) if naive is not None else None)


def forecast(
    services: list[KitchenService],
    target: date,
    *,
    dish_keys: list[str] | None = None,
    event: str = "none",
) -> dict:
    if event not in EVENTS:
        raise ValueError(f"Unknown event '{event}'")
    hist = sorted((s for s in services if s.service_date < target), key=lambda s: s.service_date)
    points = [_Point(s.service_date, s.plates_served) for s in hist]
    if len(points) < MIN_HISTORY:
        return {
            "has_data": False,
            "message": f"Log at least {MIN_HISTORY} services of this meal (or load sample data) to get a forecast.",
        }

    mult, event_label = EVENTS[event]
    base = _predict(points, target)
    expected = base * mult
    mape, sigma, naive = _backtest(points)
    sigma = max(sigma or 0.05, 0.02)
    low, high = expected * (1 - 1.28 * sigma), expected * (1 + 1.28 * sigma)
    plan_heads = math.ceil(expected * (1 + 0.84 * sigma))  # 80th percentile

    # Default menu: whatever was served at this meal on the same weekday last time.
    if not dish_keys:
        same_wd = [s for s in hist if s.service_date.weekday() == target.weekday()]
        source = same_wd[-1] if same_wd else hist[-1]
        dish_keys = [d.dish_key for d in source.dishes]

    taken: dict[str, list[float]] = defaultdict(list)
    last_cooked: dict[str, float] = {}       # last time the dish was cooked
    last_same_wd: dict[str, float] = {}      # ... on the same weekday
    for s in hist:
        for d in s.dishes:
            if s.plates_served > 0:
                taken[d.dish_key].append((d.prepared_kg - min(d.pot_leftover_kg, d.prepared_kg)) / s.plates_served)
            last_cooked[d.dish_key] = d.prepared_kg
            if s.service_date.weekday() == target.weekday():
                last_same_wd[d.dish_key] = d.prepared_kg

    cook = []
    total_saving_kg = total_saving_rs = 0.0
    for key in dish_keys:
        dish = CATALOG.get(key)
        if not dish:
            continue
        samples = taken.get(key, [])
        per_plate_kg = statistics.median(samples) if samples else dish.portion_g / 1000
        basis = "measured" if samples else "standard portion"
        cook_kg = plan_heads * per_plate_kg
        # "Usual" = what the kitchen actually cooked last time (same weekday
        # if possible): the habit the forecast is compared against.
        usual_kg = last_same_wd.get(key, last_cooked.get(key))
        saving = max(0.0, (usual_kg or 0) - cook_kg)
        total_saving_kg += saving
        total_saving_rs += saving * dish.cost_per_kg
        cook.append({
            "key": key,
            "name": dish.name,
            "cook_kg": round(cook_kg, 1),
            "per_plate_g": round(per_plate_kg * 1000),
            "standard_portion_g": dish.portion_g,
            "basis": basis,
            "usual_kg": round(usual_kg, 1) if usual_kg is not None else None,
            "saving_kg": round(saving, 1),
        })

    history = [{"date": p.day.isoformat(), "plates": p.plates} for p in points[-28:]]
    accuracy_note = None
    if mape is not None:
        accuracy_note = f"On the last {min(28, len(points) - MIN_HISTORY)} days, forecasts were off by {mape:g}% on average"
        if naive is not None:
            accuracy_note += f", versus {naive:g}% for “same as last week”"
        accuracy_note += "."

    return {
        "has_data": True,
        "target_date": target.isoformat(),
        "weekday": target.strftime("%A"),
        "event": event,
        "event_label": event_label,
        "event_multiplier": mult,
        "expected_headcount": round(expected),
        "range_low": max(0, round(low)),
        "range_high": round(high),
        "plan_for": plan_heads,
        "accuracy_mape_pct": mape,
        "naive_mape_pct": naive,
        "accuracy_note": accuracy_note,
        "history_points": len(points),
        "cook": cook,
        "saving_kg": round(total_saving_kg, 1),
        "saving_rs": round(total_saving_rs),
        "history": history,
        "method": [
            "Weekly pattern: average plates on each weekday compared with the overall average.",
            f"Recent level: a weighted average of past days, where data from {HALF_LIFE_DAYS} days ago counts half as much as yesterday.",
            "Trend: the slope over the last four weeks, capped at ±1% a day.",
            "Range: the 80% band from how wrong the method was when replayed on recent days.",
            "Cook for: the top of the likely range (80th percentile), times how much students actually take of each dish.",
        ],
    }


def next_service_date(today: date) -> date:
    return today + timedelta(days=1)
