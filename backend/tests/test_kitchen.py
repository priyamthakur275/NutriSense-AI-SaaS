"""Tests for kitchen intelligence: catalogue, menu planner (MILP), waste
analytics, forecast, sample data, tray scan, and the HTTP API."""

import io
import uuid
from datetime import date, timedelta

import pytest
from PIL import Image
from starlette.testclient import TestClient

from app.kitchen import tray_scan
from app.kitchen.catalog import CATALOG, Category, Diet, match_dish
from app.kitchen.forecast import forecast
from app.kitchen.planner import PRESETS, PlanRequest, plan_menu
from app.kitchen.waste import summarize
from app.main import app
from app.models.enums import MealType
from app.models.kitchen import KitchenService, KitchenServiceDish


# --- Catalogue ------------------------------------------------------------------

def test_diet_filters():
    assert not CATALOG["chicken_curry"].allowed_for(Diet.VEG)
    assert not CATALOG["egg_curry"].allowed_for(Diet.VEG)
    assert CATALOG["egg_curry"].allowed_for(Diet.EGG)
    assert not CATALOG["chicken_curry"].allowed_for(Diet.EGG)
    assert CATALOG["chicken_curry"].allowed_for(Diet.NON_VEG)
    assert not CATALOG["aloo_gobi"].allowed_for(Diet.JAIN)  # potato
    assert CATALOG["moong_dal"].allowed_for(Diet.JAIN)


def test_match_dish_from_free_text():
    assert match_dish("Dal Tadka").key == "dal_tadka"
    assert match_dish("roti").key == "roti"
    assert match_dish("plain steamed rice").key == "steamed_rice"
    assert match_dish("pizza") is None


# --- Menu planner ------------------------------------------------------------------

def _check_plan_obeys_rules(req: PlanRequest, result):
    preset = PRESETS[req.preset]
    assert result.feasible
    assert len(result.days) == req.days
    for day in result.days:
        cats = [CATALOG[d.key].category for d in day.dishes]
        assert cats.count(Category.GRAIN) == 1
        assert cats.count(Category.PULSE) == 1
        assert cats.count(Category.VEGETABLE) == 1
        assert cats.count(Category.BREAD) == (1 if req.include_bread else 0)
        assert 1 <= cats.count(Category.SIDE) <= 2
        assert preset.kcal_min - 0.5 <= day.totals["kcal"] <= preset.kcal_max + 0.5
        for nutrient, minimum in preset.minimums.items():
            assert day.totals[nutrient] >= minimum - 0.1, (day.day, nutrient)
        assert day.cost <= req.budget_per_plate + 0.01
        for d in day.dishes:
            assert CATALOG[d.key].allowed_for(req.diet)
    # Variety: curries at most max_repeats, never two days running.
    for key, dish in CATALOG.items():
        if dish.category in (Category.PULSE, Category.VEGETABLE):
            used = [any(d.key == key for d in day.dishes) for day in result.days]
            assert sum(used) <= req.max_repeats
            assert not any(a and b for a, b in zip(used, used[1:]))


def test_default_plan_meets_every_rule():
    req = PlanRequest(budget_per_plate=50)
    result = plan_menu(req)
    _check_plan_obeys_rules(req, result)
    assert result.solver["variables"] == 7 * len([d for d in CATALOG.values() if d.allowed_for(Diet.VEG)])
    assert any("₹" in line for line in result.explanation)


def test_cost_goal_is_no_more_expensive_than_nutrition_goal():
    cheap = plan_menu(PlanRequest(budget_per_plate=50, goal="cost"))
    rich = plan_menu(PlanRequest(budget_per_plate=50, goal="nutrition"))
    assert cheap.feasible and rich.feasible
    assert cheap.average_cost <= rich.average_cost + 0.01


@pytest.mark.parametrize("diet", [Diet.EGG, Diet.NON_VEG])
def test_other_diets(diet):
    req = PlanRequest(budget_per_plate=60, diet=diet)
    _check_plan_obeys_rules(req, plan_menu(req))


def test_jain_needs_more_repeats_and_says_so():
    tight = plan_menu(PlanRequest(budget_per_plate=50, diet=Diet.JAIN, max_repeats=2))
    assert not tight.feasible
    assert tight.blockers == ["variety"]
    req = PlanRequest(budget_per_plate=50, diet=Diet.JAIN, max_repeats=3)
    _check_plan_obeys_rules(req, plan_menu(req))


def test_infeasible_budget_reports_minimum_budget_that_works():
    result = plan_menu(PlanRequest(budget_per_plate=25))
    assert not result.feasible
    assert "budget" in result.blockers
    assert result.cheapest_feasible_cost and result.cheapest_feasible_cost > 25
    retry = PlanRequest(budget_per_plate=result.cheapest_feasible_cost + 0.01, goal="cost")
    _check_plan_obeys_rules(retry, plan_menu(retry))


def test_school_preset_without_bread():
    req = PlanRequest(preset="pm_poshan_primary", budget_per_plate=45, include_bread=False, days=6)
    _check_plan_obeys_rules(req, plan_menu(req))


def test_planner_rejects_bad_input():
    with pytest.raises(ValueError):
        plan_menu(PlanRequest(preset="nope"))
    with pytest.raises(ValueError):
        plan_menu(PlanRequest(days=9))


# --- Waste analytics ---------------------------------------------------------------

def _service(day: date, plates: int, dishes: list[tuple[str, float, float, float]], meal=MealType.LUNCH, sample=False):
    s = KitchenService(id=uuid.uuid4(), owner_id="u", service_date=day, meal_type=meal,
                       plates_served=plates, is_sample=sample)
    s.dishes = [KitchenServiceDish(dish_key=k, prepared_kg=p, pot_leftover_kg=pot, plate_waste_kg=pl)
                for k, p, pot, pl in dishes]
    return s


def test_waste_summary_arithmetic():
    services = [
        _service(date(2026, 10, 5), 100, [("steamed_rice", 20.0, 2.0, 1.0), ("dal_tadka", 15.0, 1.0, 0.5)]),
        _service(date(2026, 10, 6), 100, [("steamed_rice", 20.0, 0.0, 3.0)]),
    ]
    s = summarize(services, 28)
    t = s["totals"]
    assert t["prepared_kg"] == 55.0
    assert t["pot_leftover_kg"] == 3.0
    assert t["plate_waste_kg"] == 4.5
    assert t["eaten_kg"] == 47.5
    assert t["waste_pct"] == pytest.approx(13.6, abs=0.1)
    rice_cost = 6.0 * CATALOG["steamed_rice"].cost_per_kg
    dal_cost = 1.5 * CATALOG["dal_tadka"].cost_per_kg
    assert t["cost_wasted"] == round(rice_cost + dal_cost)
    rice = next(d for d in s["dishes"] if d["key"] == "steamed_rice")
    assert rice["plate_waste_pct"] == pytest.approx(100 * 4.0 / 38.0, abs=0.1)
    assert s["dishes"][0]["cost_wasted"] >= s["dishes"][-1]["cost_wasted"]  # sorted by ₹
    iron = next(n for n in s["nutrition"] if n["nutrient"] == "iron_mg")
    assert iron["eaten_per_plate"] < iron["served_per_plate"]
    assert len(s["insights"]) >= 3


def test_waste_summary_clamps_impossible_weights_and_handles_empty():
    assert summarize([], 28) == {"has_data": False, "days": 28}
    s = summarize([_service(date(2026, 10, 5), 10, [("roti", 2.0, 5.0, 5.0)])], 28)
    assert s["totals"]["waste_kg"] == 2.0  # never more than prepared


# --- Forecast ------------------------------------------------------------------------

def _history(days: int, end: date, weekday=400, sunday=280, noise=0):
    out = []
    for i in range(days, 0, -1):
        d = end - timedelta(days=i)
        plates = sunday if d.weekday() == 6 else weekday
        plates += (noise if i % 2 else -noise)
        out.append(_service(d, plates, [("steamed_rice", plates * 0.25, plates * 0.02, plates * 0.01),
                                         ("dal_tadka", plates * 0.17, 0.0, 0.5)]))
    return out


def test_forecast_learns_weekly_pattern():
    end = date(2026, 10, 26)  # Monday
    hist = _history(56, end)
    sunday = date(2026, 11, 1)
    f = forecast(hist, sunday)
    assert f["has_data"]
    assert f["expected_headcount"] == pytest.approx(280, rel=0.05)
    monday = forecast(hist, end)
    assert monday["expected_headcount"] == pytest.approx(400, rel=0.05)
    assert f["range_low"] <= f["expected_headcount"] <= f["range_high"]
    assert f["plan_for"] >= f["expected_headcount"]


def test_forecast_follows_a_trend():
    end = date(2026, 10, 26)
    hist = []
    for i in range(56, 0, -1):
        d = end - timedelta(days=i)
        plates = 300 + (56 - i) * 2  # +2 plates a day
        hist.append(_service(d, plates, [("roti", plates * 0.08, 0.0, 0.0)]))
    f = forecast(hist, end)
    assert f["expected_headcount"] == pytest.approx(412, rel=0.03)


def test_forecast_cook_quantities_use_measured_servings():
    end = date(2026, 10, 26)
    f = forecast(_history(56, end), end, dish_keys=["steamed_rice", "rajma"])
    rice = next(c for c in f["cook"] if c["key"] == "steamed_rice")
    rajma = next(c for c in f["cook"] if c["key"] == "rajma")
    assert rice["basis"] == "measured" and rice["per_plate_g"] == 230  # (0.25-0.02) kg/plate
    assert rajma["basis"] == "standard portion" and rajma["per_plate_g"] == 150
    assert rice["cook_kg"] == pytest.approx(f["plan_for"] * 0.23, abs=0.2)


def test_forecast_backtest_and_events():
    end = date(2026, 10, 26)
    hist = _history(56, end, noise=8)
    normal = forecast(hist, end)
    assert normal["accuracy_mape_pct"] is not None and normal["accuracy_mape_pct"] < 5
    assert "off by" in normal["accuracy_note"]
    holiday = forecast(hist, end, event="festival")
    assert holiday["expected_headcount"] == pytest.approx(normal["expected_headcount"] * 0.55, abs=2)
    with pytest.raises(ValueError):
        forecast(hist, end, event="party")


def test_forecast_needs_history():
    f = forecast(_history(3, date(2026, 10, 26)), date(2026, 10, 26))
    assert not f["has_data"] and "Log at least" in f["message"]


# --- Tray scan -----------------------------------------------------------------------

def _png(color) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (400, 300), color).save(buf, "PNG")
    return buf.getvalue()


def test_stitch_places_photos_side_by_side():
    out = Image.open(io.BytesIO(tray_scan.stitch(_png("white"), _png("gray"))))
    assert out.format == "JPEG"
    assert out.width >= 800 and out.height >= 300


@pytest.mark.asyncio
async def test_scan_trays_maps_model_output(monkeypatch):
    from app.agents.providers.base import LLMResponse

    async def fake_failover(call):
        return LLMResponse(
            content='{"items": [{"dish": "Steamed Rice", "leftover_fraction": 0.25, "confidence": 0.9},'
                    ' {"dish": "Cabbage", "leftover_fraction": 0.5, "confidence": 0.7},'
                    ' {"dish": "Mystery pudding", "leftover_fraction": 1, "confidence": 0.3}],'
                    ' "notes": "Half the cabbage came back."}',
            provider="fake", model="fake-1",
        )

    monkeypatch.setattr(tray_scan, "call_with_failover", fake_failover)
    report = await tray_scan.scan_trays(_png("white"), _png("gray"))
    rice = next(i for i in report["items"] if i["key"] == "steamed_rice")
    assert rice["leftover_pct"] == 25 and rice["leftover_g"] == 50
    cabbage = next(i for i in report["items"] if i["key"] == "cabbage_poriyal")
    assert cabbage["leftover_g"] == 60
    unknown = next(i for i in report["items"] if i["key"] is None)
    assert unknown["leftover_g"] is None
    assert report["plate_leftover_g"] == 110
    assert report["provider"] == "fake"


# --- HTTP API --------------------------------------------------------------------------

def _auth(client: TestClient, email: str) -> dict:
    resp = client.post("/api/v1/auth/register", json={
        "email": email, "full_name": "Kitchen Tester", "password": "Str0ng!Pass#2026",
    })
    assert resp.status_code == 201, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_kitchen_api_end_to_end():
    client = TestClient(app)
    h = _auth(client, f"kitchen.{uuid.uuid4().hex[:8]}@test.com")

    assert client.get("/api/v1/kitchen/waste/summary").status_code == 401
    assert client.get("/api/v1/kitchen/waste/summary", headers=h).json()["has_data"] is False

    cat = client.get("/api/v1/kitchen/catalog", headers=h).json()
    assert len(cat["dishes"]) == len(CATALOG) and len(cat["presets"]) == 3

    created = client.post("/api/v1/kitchen/sample-data", headers=h).json()["created"]
    assert created == 112
    summary = client.get("/api/v1/kitchen/waste/summary?days=28", headers=h).json()
    assert summary["has_data"] and summary["is_sample"]
    assert 5 < summary["totals"]["waste_pct"] < 30

    fc = client.get("/api/v1/kitchen/forecast?meal_type=lunch", headers=h).json()
    assert fc["has_data"] and fc["expected_headcount"] > 0 and fc["cook"]
    bad = client.get("/api/v1/kitchen/forecast?dishes=pizza", headers=h)
    assert bad.status_code == 422

    plan = client.post("/api/v1/kitchen/menu-plan", headers=h, json={"budget_per_plate": 50})
    assert plan.status_code == 200 and plan.json()["feasible"]
    assert client.post("/api/v1/kitchen/menu-plan", headers=h, json={"goal": "fast"}).status_code == 422

    service = {
        "service_date": date.today().isoformat(), "meal_type": "lunch", "plates_served": 120,
        "dishes": [{"dish_key": "steamed_rice", "prepared_kg": 30, "pot_leftover_kg": 3, "plate_waste_kg": 2}],
    }
    r = client.post("/api/v1/kitchen/services", headers=h, json=service)
    assert r.status_code == 201 and r.json()["is_sample"] is False
    service_id = r.json()["id"]

    too_much = {**service, "dishes": [{"dish_key": "roti", "prepared_kg": 5, "pot_leftover_kg": 4, "plate_waste_kg": 2}]}
    assert client.post("/api/v1/kitchen/services", headers=h, json=too_much).status_code == 422
    unknown = {**service, "dishes": [{"dish_key": "pizza", "prepared_kg": 5}]}
    assert client.post("/api/v1/kitchen/services", headers=h, json=unknown).status_code == 422

    # Another user cannot delete it.
    other = _auth(client, f"kitchen.{uuid.uuid4().hex[:8]}@test.com")
    assert client.delete(f"/api/v1/kitchen/services/{service_id}", headers=other).status_code == 404
    assert client.get("/api/v1/kitchen/waste/summary", headers=other).json()["has_data"] is False

    removed = client.delete("/api/v1/kitchen/sample-data", headers=h).json()["removed"]
    assert removed == 112
    remaining = client.get("/api/v1/kitchen/services?days=7", headers=h).json()
    assert [s["id"] for s in remaining] == [service_id]
    assert client.delete(f"/api/v1/kitchen/services/{service_id}", headers=h).status_code == 204
