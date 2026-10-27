"""Catalogue of common Indian institutional dishes.

Every number here is *per 100 g of the cooked dish* and is an approximation
built from the Indian Food Composition Tables (IFCT 2017, ICMR-NIN) applied
to standard canteen recipes (Jain-friendly dishes assume tempering without
onion or garlic). Cost is an approximate 2026 institutional cost
per kg of cooked food (ingredients + fuel), in rupees.

The catalogue is deliberately small and explicit: the menu planner, the waste
tracker and the forecast all read from it, so a reviewer can trace any number
on screen back to one line in this file.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    GRAIN = "grain"          # rice dishes, ragi mudde
    BREAD = "bread"          # roti, bajra roti
    PULSE = "pulse"          # dal, sambar, rajma, chana
    VEGETABLE = "vegetable"  # sabzi / poriyal / curries
    SIDE = "side"            # curd, salad, fruit, egg, chikki


class Diet(str, Enum):
    VEG = "veg"          # vegetarian (no egg, meat or fish)
    JAIN = "jain"        # vegetarian, no onion/garlic/root vegetables
    EGG = "egg"          # vegetarian + eggs
    NON_VEG = "non_veg"  # everything


@dataclass(frozen=True)
class Dish:
    key: str
    name: str
    category: Category
    portion_g: int          # standard serving per plate
    kcal: float             # per 100 g cooked
    protein_g: float
    iron_mg: float
    calcium_mg: float
    fibre_g: float
    cost_per_kg: float      # ₹ per kg cooked
    contains_egg: bool = False
    contains_meat: bool = False
    jain_ok: bool = False   # no onion, garlic or root vegetables

    def allowed_for(self, diet: Diet) -> bool:
        if diet == Diet.NON_VEG:
            return True
        if self.contains_meat:
            return False
        if diet == Diet.EGG:
            return True
        if self.contains_egg:
            return False
        if diet == Diet.JAIN:
            return self.jain_ok
        return True  # VEG

    def per_portion(self, nutrient: str) -> float:
        return getattr(self, nutrient) * self.portion_g / 100.0

    @property
    def cost_per_portion(self) -> float:
        return self.cost_per_kg * self.portion_g / 1000.0


NUTRIENTS = ("kcal", "protein_g", "iron_mg", "calcium_mg", "fibre_g")

_DISHES: list[Dish] = [
    # --- Grains ---
    Dish("steamed_rice", "Steamed rice", Category.GRAIN, 200, 130, 2.7, 0.2, 10, 0.4, 32, jain_ok=True),
    Dish("jeera_rice", "Jeera rice", Category.GRAIN, 200, 150, 2.8, 0.4, 14, 0.6, 42, jain_ok=True),
    Dish("veg_pulao", "Veg pulao", Category.GRAIN, 200, 145, 3.2, 0.7, 20, 1.2, 55),
    Dish("lemon_rice", "Lemon rice", Category.GRAIN, 200, 160, 3.0, 0.6, 15, 0.8, 45, jain_ok=True),
    Dish("ragi_mudde", "Ragi mudde", Category.GRAIN, 200, 110, 2.4, 1.2, 110, 3.5, 40, jain_ok=True),
    # --- Breads ---
    Dish("roti", "Roti (2)", Category.BREAD, 80, 275, 8.5, 2.6, 30, 4.0, 70, jain_ok=True),
    Dish("bajra_roti", "Bajra roti (2)", Category.BREAD, 80, 280, 8.0, 5.0, 30, 5.0, 75, jain_ok=True),
    # --- Pulses ---
    Dish("dal_tadka", "Dal tadka", Category.PULSE, 150, 110, 6.0, 1.3, 25, 2.5, 110, jain_ok=True),
    Dish("moong_dal", "Moong dal", Category.PULSE, 150, 100, 6.5, 1.2, 25, 2.2, 115, jain_ok=True),
    Dish("masoor_dal", "Masoor dal", Category.PULSE, 150, 105, 7.0, 2.0, 20, 2.5, 105, jain_ok=True),
    Dish("rajma", "Rajma", Category.PULSE, 150, 125, 7.5, 2.0, 40, 5.0, 130),
    Dish("chana_masala", "Chana masala", Category.PULSE, 150, 150, 7.5, 2.5, 50, 6.0, 120),
    Dish("sambar", "Sambar", Category.PULSE, 200, 75, 3.5, 1.0, 35, 2.5, 70),
    # --- Vegetables ---
    Dish("aloo_gobi", "Aloo gobi", Category.VEGETABLE, 120, 95, 2.2, 0.7, 25, 2.5, 80),
    Dish("mixed_veg", "Mixed veg", Category.VEGETABLE, 120, 85, 2.5, 1.0, 40, 3.0, 85),
    Dish("bhindi_fry", "Bhindi fry", Category.VEGETABLE, 120, 110, 2.0, 0.6, 70, 3.0, 100, jain_ok=True),
    Dish("cabbage_poriyal", "Cabbage poriyal", Category.VEGETABLE, 120, 80, 1.8, 0.6, 45, 2.5, 65, jain_ok=True),
    Dish("beans_poriyal", "Beans poriyal", Category.VEGETABLE, 120, 85, 2.2, 1.0, 45, 3.5, 90, jain_ok=True),
    Dish("lauki_sabzi", "Lauki sabzi", Category.VEGETABLE, 120, 60, 1.5, 0.5, 25, 1.5, 60, jain_ok=True),
    Dish("methi_aloo", "Methi aloo", Category.VEGETABLE, 120, 105, 2.6, 2.4, 80, 3.0, 85),
    Dish("palak_paneer", "Palak paneer", Category.VEGETABLE, 120, 160, 8.0, 2.8, 210, 2.0, 220),
    Dish("soya_curry", "Soya chunk curry", Category.VEGETABLE, 120, 120, 10.0, 3.0, 60, 3.5, 110),
    Dish("egg_curry", "Egg curry", Category.VEGETABLE, 120, 150, 9.5, 1.5, 45, 0.8, 160, contains_egg=True),
    Dish("chicken_curry", "Chicken curry", Category.VEGETABLE, 120, 165, 15.0, 1.2, 20, 0.8, 300, contains_meat=True),
    # --- Sides ---
    Dish("curd", "Curd", Category.SIDE, 100, 60, 3.1, 0.2, 120, 0.0, 80, jain_ok=True),
    Dish("buttermilk", "Buttermilk", Category.SIDE, 200, 25, 1.2, 0.1, 60, 0.0, 30, jain_ok=True),
    Dish("cucumber_salad", "Cucumber salad", Category.SIDE, 60, 18, 0.8, 0.3, 18, 0.8, 50, jain_ok=True),
    Dish("sprouts_salad", "Sprouts salad", Category.SIDE, 80, 60, 4.0, 1.2, 20, 2.0, 90),
    Dish("banana", "Banana", Category.SIDE, 100, 89, 1.1, 0.3, 5, 2.6, 50, jain_ok=True),
    Dish("guava", "Guava", Category.SIDE, 100, 68, 2.6, 0.3, 18, 5.4, 70, jain_ok=True),
    Dish("peanut_chikki", "Peanut chikki", Category.SIDE, 30, 500, 13.0, 2.8, 60, 4.0, 200, jain_ok=True),
    Dish("boiled_egg", "Boiled egg", Category.SIDE, 50, 155, 13.0, 1.2, 50, 0.0, 140, contains_egg=True),
]

CATALOG: dict[str, Dish] = {d.key: d for d in _DISHES}


def get_dish(key: str) -> Dish:
    try:
        return CATALOG[key]
    except KeyError as exc:
        raise KeyError(f"Unknown dish '{key}'") from exc


def match_dish(name: str) -> Dish | None:
    """Best-effort match of a free-text dish name (e.g. from the vision model)
    to a catalogue entry: exact key, exact name, then word overlap."""
    if not name:
        return None
    norm = name.strip().lower().replace("-", " ").replace("_", " ")
    for d in _DISHES:
        if norm in (d.key.replace("_", " "), d.name.lower(), d.name.lower().split(" (")[0]):
            return d
    words = set(norm.split())
    best, best_score = None, 0
    for d in _DISHES:
        dish_words = set(d.name.lower().replace("(", " ").replace(")", " ").split()) | set(d.key.split("_"))
        score = len(words & dish_words)
        if score > best_score:
            best, best_score = d, score
    return best if best_score > 0 else None
