"""Kitchen intelligence: food-waste tracking, menu planning, cooking forecast.

Every endpoint is scoped to the signed-in user's own kitchen logs, so any
account (including a reviewer's fresh demo account) can try the features.
"""

from dataclasses import asdict
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.file_validation import validate_upload_file
from app.core.rate_limit import RateLimiter
from app.db.session import get_db
from app.kitchen import forecast as forecast_mod
from app.kitchen.catalog import CATALOG, NUTRIENTS
from app.kitchen.planner import PRESETS, PlanRequest, plan_menu
from app.kitchen.sample_data import clear_sample, generate_sample
from app.kitchen.tray_scan import scan_trays
from app.kitchen.waste import services_in_window, summarize
from app.models.enums import MealType
from app.models.kitchen import KitchenService, KitchenServiceDish
from app.models.user import User
from app.schemas.kitchen import MenuPlanIn, ServiceIn, ServiceOut

router = APIRouter(prefix="/kitchen", tags=["Kitchen intelligence"])


@router.get("/catalog")
def catalog(_: User = Depends(get_current_user)) -> dict:
    """Dish catalogue and nutrition-target presets used by every kitchen feature."""
    return {
        "dishes": [
            {
                "key": d.key, "name": d.name, "category": d.category.value, "portion_g": d.portion_g,
                "cost_per_portion": round(d.cost_per_portion, 2), "cost_per_kg": d.cost_per_kg,
                "per_portion": {n: round(d.per_portion(n), 1) for n in NUTRIENTS},
                "veg": not (d.contains_egg or d.contains_meat), "jain_ok": d.jain_ok,
            }
            for d in CATALOG.values()
        ],
        "presets": [
            {"key": p.key, "label": p.label, "source": p.source, "kcal_min": p.kcal_min,
             "kcal_max": p.kcal_max, "minimums": p.minimums}
            for p in PRESETS.values()
        ],
        "events": [{"key": k, "label": v[1], "multiplier": v[0]} for k, v in forecast_mod.EVENTS.items()],
    }


# --- Service logs -----------------------------------------------------------

@router.post("/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
def log_service(payload: ServiceIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = KitchenService(
        owner_id=user.id, service_date=payload.service_date, meal_type=payload.meal_type,
        plates_served=payload.plates_served, notes=payload.notes, is_sample=False,
    )
    for d in payload.dishes:
        service.dishes.append(KitchenServiceDish(**d.model_dump()))
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get("/services", response_model=list[ServiceOut])
def list_services(
    days: int = Query(14, ge=1, le=120),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    end = date.today()
    return list(reversed(services_in_window(db, user.id, end - timedelta(days=days), end)))


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service = db.get(KitchenService, service_id)
    if not service or service.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()


@router.post("/sample-data")
def load_sample_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    """Replace this account's sample logs with eight fresh weeks of sample data."""
    created = generate_sample(db, user.id)
    db.commit()
    return {"created": created}


@router.delete("/sample-data")
def remove_sample_data(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    removed = clear_sample(db, user.id)
    db.commit()
    return {"removed": removed}


# --- Waste ------------------------------------------------------------------

@router.get("/waste/summary")
def waste_summary(
    days: int = Query(28, ge=7, le=120),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    end = date.today()
    return summarize(services_in_window(db, user.id, end - timedelta(days=days), end), days)


@router.post(
    "/waste/tray-scan",
    dependencies=[Depends(RateLimiter(times=10, seconds=60, scope="kitchen_tray_scan"))],
)
async def tray_scan(
    before: UploadFile = File(..., description="Tray photo when served"),
    after: UploadFile = File(..., description="Same tray when returned"),
    _: User = Depends(get_current_user),
) -> dict:
    """Estimate how much of each dish was left on a plate from two photos."""
    image_types = {"image/jpeg", "image/png", "image/webp"}
    before_bytes = await validate_upload_file(before, allowed_content_types=image_types)
    after_bytes = await validate_upload_file(after, allowed_content_types=image_types)
    return await scan_trays(before_bytes, after_bytes)


# --- Menu planner -------------------------------------------------------------

@router.post("/menu-plan", dependencies=[Depends(RateLimiter(times=20, seconds=60, scope="kitchen_menu_plan"))])
def menu_plan(payload: MenuPlanIn, _: User = Depends(get_current_user)) -> dict:
    try:
        result = plan_menu(PlanRequest(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return asdict(result)


# --- Forecast -------------------------------------------------------------------

@router.get("/forecast")
def cooking_forecast(
    target_date: date | None = Query(None, description="Defaults to tomorrow"),
    meal_type: MealType = Query(MealType.LUNCH),
    dishes: str | None = Query(None, description="Comma-separated dish keys; defaults to last same-weekday menu"),
    event: str = Query("none"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    target = target_date or forecast_mod.next_service_date(date.today())
    services = [
        s for s in services_in_window(db, user.id, target - timedelta(days=56), target - timedelta(days=1))
        if s.meal_type == meal_type
    ]
    keys = [k.strip() for k in dishes.split(",") if k.strip()] if dishes else None
    if keys:
        unknown = [k for k in keys if k not in CATALOG]
        if unknown:
            raise HTTPException(status_code=422, detail=f"Unknown dishes: {', '.join(unknown)}")
    try:
        return forecast_mod.forecast(services, target, dish_keys=keys, event=event)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
