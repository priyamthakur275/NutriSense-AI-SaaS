"""Budget-aware weekly menu planner.

Plain-English version (what to tell a recruiter):
    "Given a budget per plate, a diet rule and nutrition targets, the planner
    picks which dishes to serve on each day. It's set up as an optimisation
    problem: every (day, dish) pair is a yes/no choice, the rules become
    linear constraints, and a solver finds the best valid combination in
    milliseconds. If no menu can satisfy the rules, it tells you which rule
    is the blocker and what it would take to relax it."

Technical version:
    Mixed-integer linear program (MILP) solved with SciPy's HiGHS backend.
      variables  x[d, j] ∈ {0, 1}     dish j served on day d
      per day    exactly one grain, one pulse, one vegetable;
                 one bread (optional); 1-2 sides
                 Σ nutrient_j·x[d,j] ≥ target   for each nutrient target
                 Σ kcal_j·x[d,j]     ≤ kcal_max
                 Σ cost_j·x[d,j]     ≤ budget per plate
      per week   each pulse/vegetable at most `max_repeats` times,
                 never on two consecutive days; grains and sides at
                 most `max_repeats + 1` times
      objective  "nutrition": maximise Σ (nutrient / target) over the week
                              (capped per nutrient so one dish can't dominate)
                 "cost":      minimise total cost
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.kitchen.catalog import CATALOG, NUTRIENTS, Category, Diet, Dish

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

NUTRIENT_LABELS = {
    "kcal": ("Energy", "kcal"),
    "protein_g": ("Protein", "g"),
    "iron_mg": ("Iron", "mg"),
    "calcium_mg": ("Calcium", "mg"),
    "fibre_g": ("Fibre", "g"),
}


@dataclass(frozen=True)
class TargetPreset:
    key: str
    label: str
    source: str
    kcal_min: float
    kcal_max: float
    minimums: dict[str, float]


# PM POSHAN figures are the scheme's published per-meal norms. The hostel
# preset is roughly one third of ICMR-NIN 2020 daily needs for young adults.
PRESETS: dict[str, TargetPreset] = {
    p.key: p
    for p in [
        TargetPreset(
            "pm_poshan_primary", "School midday meal (classes 1-5)", "PM POSHAN norm: 450 kcal, 12 g protein",
            450, 750, {"protein_g": 12},
        ),
        TargetPreset(
            "pm_poshan_upper", "School midday meal (classes 6-8)", "PM POSHAN norm: 700 kcal, 20 g protein",
            700, 1000, {"protein_g": 20},
        ),
        TargetPreset(
            "hostel_lunch", "College hostel lunch", "About 1/3 of ICMR-NIN 2020 daily needs, young adults",
            700, 1050, {"protein_g": 18, "iron_mg": 6, "calcium_mg": 250, "fibre_g": 8},
        ),
    ]
}


@dataclass
class PlanRequest:
    preset: str = "hostel_lunch"
    budget_per_plate: float = 45.0
    diet: Diet = Diet.VEG
    days: int = 7
    include_bread: bool = True
    max_repeats: int = 2
    goal: str = "nutrition"  # "nutrition" | "cost"
    exclude: list[str] = field(default_factory=list)


@dataclass
class PlannedDish:
    key: str
    name: str
    category: str
    portion_g: int
    cost: float


@dataclass
class PlannedDay:
    day: str
    dishes: list[PlannedDish]
    totals: dict[str, float]
    cost: float


@dataclass
class PlanResult:
    feasible: bool
    days: list[PlannedDay]
    average_cost: float
    targets: dict[str, dict]
    explanation: list[str]
    solver: dict
    blockers: list[str] = field(default_factory=list)
    cheapest_feasible_cost: float | None = None   # a menu is proven to exist at this budget
    min_budget_lower_bound: float | None = None   # no menu exists below this budget


class _Model:
    """Builds the constraint matrix for one request. Kept as a small class so
    the infeasibility diagnosis can rebuild it with individual rule groups
    switched off."""

    def __init__(self, req: PlanRequest, preset: TargetPreset, dishes: list[Dish]):
        self.req, self.preset, self.dishes = req, preset, dishes
        self.D, self.J = req.days, len(dishes)

    def idx(self, d: int, j: int) -> int:
        return d * self.J + j

    def build(self, *, skip: frozenset[str] = frozenset(), budget: float | None = None):
        import numpy as np

        req, D, J = self.req, self.D, self.J
        n = D * J
        rows, lo, hi = [], [], []

        def add(coeffs: dict[int, float], lower: float, upper: float):
            row = np.zeros(n)
            for k, v in coeffs.items():
                row[k] = v
            rows.append(row)
            lo.append(lower)
            hi.append(upper)

        cat_bounds = {
            Category.GRAIN: (1, 1),
            Category.PULSE: (1, 1),
            Category.VEGETABLE: (1, 1),
            Category.BREAD: (1, 1) if req.include_bread else (0, 0),
            Category.SIDE: (1, 2),
        }
        for d in range(D):
            for cat, (a, b) in cat_bounds.items():
                add({self.idx(d, j): 1 for j, dish in enumerate(self.dishes) if dish.category == cat}, a, b)
            if "energy" not in skip:
                add({self.idx(d, j): dish.per_portion("kcal") for j, dish in enumerate(self.dishes)},
                    self.preset.kcal_min, self.preset.kcal_max)
            for nutrient, minimum in self.preset.minimums.items():
                if nutrient in skip:
                    continue
                add({self.idx(d, j): dish.per_portion(nutrient) for j, dish in enumerate(self.dishes)},
                    minimum, np.inf)
            if "budget" not in skip:
                add({self.idx(d, j): dish.cost_per_portion for j, dish in enumerate(self.dishes)},
                    0, budget if budget is not None else req.budget_per_plate)

        if "variety" not in skip:
            for j, dish in enumerate(self.dishes):
                if dish.category in (Category.PULSE, Category.VEGETABLE):
                    # Main curries: repeat limit, never two days running.
                    add({self.idx(d, j): 1 for d in range(D)}, 0, req.max_repeats)
                    for d in range(D - 1):
                        add({self.idx(d, j): 1, self.idx(d + 1, j): 1}, 0, 1)
                elif dish.category in (Category.GRAIN, Category.SIDE):
                    # Staples and sides may repeat more, but not every day.
                    add({self.idx(d, j): 1 for d in range(D)}, 0, req.max_repeats + 1)
                elif dish.category == Category.BREAD:
                    add({self.idx(d, j): 1 for d in range(D)}, 0, req.max_repeats + 2)

        return np.array(rows), np.array(lo), np.array(hi)

    def objective(self, goal: str):
        import numpy as np

        c = np.zeros(self.D * self.J)
        if goal == "feasibility":
            return c
        for d in range(self.D):
            for j, dish in enumerate(self.dishes):
                if goal == "cost":
                    c[self.idx(d, j)] = dish.cost_per_portion
                else:
                    # Reward each nutrient relative to its target, capped at
                    # 1.5x per dish so chikki can't "buy" the whole score;
                    # tiny cost term breaks ties towards the cheaper menu.
                    score = 0.0
                    for nutrient, target in self.preset.minimums.items():
                        score += min(dish.per_portion(nutrient) / target, 1.5)
                    c[self.idx(d, j)] = -score + 0.002 * dish.cost_per_portion
        return c

    def improve(self, x, c, *, skip: frozenset[str] = frozenset(), key=None, max_passes: int = 8):
        """Local search: swap one dish for another of the same category on
        one day whenever every rule still holds and the score improves.
        Each candidate swap is checked in O(rules) using the column
        difference A[:, new] - A[:, old], so this runs in milliseconds even
        on a slow server. `key` overrides the score (used to lower the most
        expensive day when searching for a minimum budget)."""
        import numpy as np

        A, lo, hi = self.build(skip=skip)
        x = (np.asarray(x) > 0.5).astype(float)
        Ax = A @ x
        score = key or (lambda v: float(c @ v))
        best = score(x)
        cats = [dish.category for dish in self.dishes]
        for _ in range(max_passes):
            improved = False
            for d in range(self.D):
                for j_old in range(self.J):
                    i_old = self.idx(d, j_old)
                    if x[i_old] < 0.5:
                        continue
                    for j_new in range(self.J):
                        if j_new == j_old or cats[j_new] != cats[j_old]:
                            continue
                        i_new = self.idx(d, j_new)
                        if x[i_new] > 0.5:
                            continue
                        new_Ax = Ax - A[:, i_old] + A[:, i_new]
                        if np.any(new_Ax < lo - 1e-6) or np.any(new_Ax > hi + 1e-6):
                            continue
                        x[i_old], x[i_new] = 0.0, 1.0
                        val = score(x)
                        if val < best - 1e-9:
                            best, Ax, improved = val, new_Ax, True
                            break
                        x[i_old], x[i_new] = 1.0, 0.0
                    if improved:
                        break
            if not improved:
                break
        return x, best

    def day_costs(self, x) -> list[float]:
        return [
            sum(self.dishes[j].cost_per_portion for j in range(self.J) if x[self.idx(d, j)] > 0.5)
            for d in range(self.D)
        ]

    def min_budget(self, time_limit: float = 2.5) -> tuple[float, float] | None:
        """Smallest per-plate budget for which a valid menu exists: add one
        continuous variable z ≥ each day's cost and minimise z. Returns
        (guaranteed, lower_bound): a menu is proven to exist at
        `guaranteed`, and none exists below `lower_bound`. They are equal
        when the solver finishes; on a slow server they bracket the answer."""
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp

        A, lo, hi = self.build(skip=frozenset({"budget"}))
        n = self.D * self.J
        A = np.hstack([A, np.zeros((A.shape[0], 1))])
        cost_rows = []
        for d in range(self.D):
            row = np.zeros(n + 1)
            for j, dish in enumerate(self.dishes):
                row[self.idx(d, j)] = dish.cost_per_portion
            row[n] = -1.0  # day cost - z <= 0
            cost_rows.append(row)
        A = np.vstack([A, np.array(cost_rows)])
        lo = np.concatenate([lo, np.full(self.D, -np.inf)])
        hi = np.concatenate([hi, np.zeros(self.D)])
        c = np.zeros(n + 1)
        c[n] = 1.0
        res = milp(
            c=c,
            constraints=LinearConstraint(A, lo, hi),
            integrality=np.concatenate([np.ones(n), [0]]),
            bounds=Bounds(np.zeros(n + 1), np.concatenate([np.ones(n), [np.inf]])),
            options={"time_limit": time_limit, "mip_rel_gap": 0.01},
        )
        if res.status in (0, 1) and res.x is not None:
            x = res.x[:n]
            # Polish: lower the most expensive day with local swaps.
            x, _ = self.improve(
                x, None, skip=frozenset({"budget"}),
                key=lambda v: max(self.day_costs(v)) + 1e-4 * sum(self.day_costs(v)),
            )
            upper = float(np.ceil(max(self.day_costs(x)) * 100) / 100)
            lower = float(getattr(res, "mip_dual_bound", None) or upper)
            if res.status == 0:
                lower = upper
            return upper, float(np.floor(min(lower, upper) * 100) / 100)
        return None

    def solve(self, goal: str, time_limit: float = 3.0, gap: float = 0.02, **build_kwargs):
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp

        A, lo, hi = self.build(**build_kwargs)
        res = milp(
            c=self.objective(goal),
            constraints=LinearConstraint(A, lo, hi),
            integrality=np.ones(self.D * self.J),
            bounds=Bounds(0, 1),
            options={"time_limit": time_limit, "mip_rel_gap": gap},
        )
        return res, A.shape


def _candidate_dishes(req: PlanRequest) -> list[Dish]:
    excluded = set(req.exclude)
    return [d for d in CATALOG.values() if d.allowed_for(req.diet) and d.key not in excluded]


_CACHE: dict[tuple, PlanResult] = {}
_CACHE_MAX = 128


def _cache_key(req: PlanRequest) -> tuple:
    return (req.preset, round(req.budget_per_plate, 2), req.diet, req.days, req.include_bread,
            req.max_repeats, req.goal, tuple(sorted(req.exclude)))


def plan_menu(req: PlanRequest) -> PlanResult:
    """Cached wrapper: the same request always gets the same plan back
    instantly (menus only depend on the request and the catalogue)."""
    key = _cache_key(req)
    if key not in _CACHE:
        if len(_CACHE) >= _CACHE_MAX:
            _CACHE.pop(next(iter(_CACHE)))
        _CACHE[key] = _plan_menu(req)
    return _CACHE[key]


def warm_up() -> None:
    """Pre-solve the default request (and import SciPy) so the first visitor
    after a cold start doesn't wait for it."""
    try:
        plan_menu(PlanRequest(budget_per_plate=50))
    except Exception:  # never let a warm-up failure affect startup
        pass


def _plan_menu(req: PlanRequest) -> PlanResult:
    if req.preset not in PRESETS:
        raise ValueError(f"Unknown target preset '{req.preset}'")
    if not 1 <= req.days <= 7:
        raise ValueError("days must be between 1 and 7")
    preset = PRESETS[req.preset]
    dishes = _candidate_dishes(req)
    model = _Model(req, preset, dishes)

    # Three steps, so even a slow server returns a good, valid menu fast:
    #   1. feasibility MILP: find *any* menu that satisfies every rule, or
    #      prove that none exists;
    #   2. local search: swap dishes while every rule still holds (ms);
    #   3. optimisation MILP for a bounded time; keep whichever is better.
    import numpy as np

    started = time.perf_counter()
    feas, shape = model.solve("feasibility", time_limit=4.0, gap=0.0)
    res, status, x_best = feas, "", None
    if feas.x is not None:
        c = model.objective(req.goal)
        x_best, best_val = model.improve(feas.x, c)
        status = "valid, improved by local search"
        opt, _ = model.solve(req.goal, time_limit=3.0, gap=0.05)
        if opt.x is not None:
            x_opt = (opt.x > 0.5).astype(float)
            if float(c @ x_opt) <= best_val + 1e-9:
                x_best = x_opt
                status = "optimal (within 5%)" if opt.status == 0 else "best found in time limit"
    res_x = None if x_best is None else np.asarray(x_best)
    elapsed_ms = (time.perf_counter() - started) * 1000

    targets = {
        "kcal": {"label": "Energy", "unit": "kcal", "min": preset.kcal_min, "max": preset.kcal_max},
        **{
            k: {"label": NUTRIENT_LABELS[k][0], "unit": NUTRIENT_LABELS[k][1], "min": v, "max": None}
            for k, v in preset.minimums.items()
        },
    }
    solver = {
        "method": "Mixed-integer linear programming (SciPy / HiGHS) + local search",
        "variables": int(shape[1]),
        "constraints": int(shape[0]),
        "candidate_dishes": len(dishes),
        "solve_ms": round(elapsed_ms, 1),
        "status": status if res_x is not None else ("infeasible" if feas.status == 2 else "no menu found in time"),
    }

    if res_x is None:
        blockers, cheapest = _diagnose(model, req)
        bounds = getattr(model, "min_budget_bounds", None)
        return PlanResult(
            feasible=False, days=[], average_cost=0.0, targets=targets,
            explanation=_infeasible_text(req, preset, blockers, bounds, proven=feas.status == 2),
            solver=solver, blockers=blockers, cheapest_feasible_cost=cheapest,
            min_budget_lower_bound=bounds[1] if bounds else None,
        )

    days: list[PlannedDay] = []
    for d in range(req.days):
        chosen = [dishes[j] for j in range(len(dishes)) if res_x[model.idx(d, j)] > 0.5]
        order = [Category.GRAIN, Category.BREAD, Category.PULSE, Category.VEGETABLE, Category.SIDE]
        chosen.sort(key=lambda x: order.index(x.category))
        totals = {n: round(sum(x.per_portion(n) for x in chosen), 1) for n in NUTRIENTS}
        cost = round(sum(x.cost_per_portion for x in chosen), 2)
        days.append(PlannedDay(
            day=DAY_NAMES[d],
            dishes=[PlannedDish(x.key, x.name, x.category.value, x.portion_g, round(x.cost_per_portion, 2)) for x in chosen],
            totals=totals, cost=cost,
        ))

    avg = round(sum(d.cost for d in days) / len(days), 2)
    return PlanResult(
        feasible=True, days=days, average_cost=avg, targets=targets,
        explanation=_feasible_text(req, preset, days, avg, solver),
        solver=solver,
    )


def _diagnose(model: _Model, req: PlanRequest) -> tuple[list[str], float | None]:
    """Find which rule groups block a solution by switching each one off in
    turn, and compute the cheapest budget that would work."""
    groups = ["budget", "variety", "energy", *model.preset.minimums.keys()]
    blockers = []
    for g in groups:
        res, _ = model.solve("feasibility", time_limit=1.0, gap=0.0, skip=frozenset({g}))
        if res.status in (0, 1) and res.x is not None:
            blockers.append(g)

    bounds = model.min_budget() if "budget" in blockers else None
    cheapest = bounds[0] if bounds else None
    model.min_budget_bounds = bounds
    return blockers, cheapest


def _rule_name(group: str) -> str:
    return {
        "budget": "the budget per plate",
        "variety": "the variety rule (try allowing each dish one more time per week)",
        "energy": "the energy range",
    }.get(group, f"the {NUTRIENT_LABELS.get(group, (group,))[0].lower()} target")


def _infeasible_text(req, preset, blockers, bounds, proven: bool = True) -> list[str]:
    where = (f"for “{preset.label}” at ₹{req.budget_per_plate:.0f} per plate "
             f"with a {req.diet.value.replace('_', '-')} diet")
    lines = [
        f"No {req.days}-day menu meets every rule {where}." if proven else
        f"The solver couldn't find a {req.days}-day menu that meets every rule {where} within its time limit. "
        "This budget is right at the edge of what's possible."
    ]
    if blockers:
        lines.append("Relaxing any one of these would make a menu possible: " + "; ".join(_rule_name(b) for b in blockers) + ".")
    if bounds and "budget" in blockers:
        upper, lower = bounds
        if upper - lower < 0.5:
            lines.append(f"The lowest budget that meets every nutrition and variety rule is ₹{upper:.2f} per plate.")
        else:
            lines.append(
                f"A menu that meets every rule exists at ₹{upper:.2f} per plate. The solver also proved "
                f"none exists below ₹{lower:.2f}, so the true minimum is in between."
            )
    if not blockers:
        lines.append("More than one rule conflicts at once. Try a higher budget together with a wider diet option.")
    return lines


def _feasible_text(req, preset, days, avg, solver) -> list[str]:
    lines = [
        f"Every day meets “{preset.label}” ({preset.source}) and stays within ₹{req.budget_per_plate:.0f} per plate; "
        f"the week averages ₹{avg:.2f}.",
    ]
    for nutrient, minimum in preset.minimums.items():
        low = min(days, key=lambda d: d.totals[nutrient])
        label, unit = NUTRIENT_LABELS[nutrient]
        lines.append(
            f"{label}: lowest day is {low.day} with {low.totals[nutrient]:g} {unit} (target {minimum:g} {unit})."
        )
    lines.append(
        f"The solver checked {solver['candidate_dishes']} dishes across {req.days} days "
        f"({solver['variables']} yes/no choices, {solver['constraints']} rules) in "
        + (f"{solver['solve_ms'] / 1000:.1f} s." if solver["solve_ms"] >= 1000 else f"{solver['solve_ms']:.0f} ms.")
    )
    if req.goal == "cost":
        lines.append("Goal: cheapest menu that still meets every target.")
    else:
        lines.append("Goal: most nutrition for the budget, scored against each target.")
    return lines
