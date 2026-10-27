# Kitchen intelligence: waste tracking, menu planner, cooking forecast

Three features that work as one loop:

**measure what is eaten → plan a better menu → cook the right amount**

Indian hostel, school and hospital kitchens waste 10–25% of the food they cook,
and the meal that was *served* is not the meal that was *eaten*. These features
make that visible and fix it with maths a kitchen manager can trust.

---

## 1. Food waste tracker (`/dashboard/waste`)

**What it does.** After each meal the kitchen records, per dish, three weights:
cooked, left in the pot, and scraped off returned plates. The dashboard turns
that into waste %, rupees lost, portions thrown away, which dishes are the
problem, and how much nutrition students actually ate.

**The idea that makes it different.** It separates the two kinds of waste:

| | What it means | What fixes it |
|---|---|---|
| Left in the pot | Cooked too much | Cook to a forecast (feature 3) |
| Left on plates | Served but not eaten | Change the recipe, the portion, or the menu (feature 2) |

It also shows a **nutrition gap**: plates were served 6.7 mg of iron, students
ate 6.2 mg. Waste isn't only money.

**AI tray scan.** Upload a photo of the tray when served and when returned.
Both photos are stitched side by side into one image and sent to the vision
model (Gemini/OpenAI through the app's provider-failover layer), which returns
JSON: each dish and the fraction left. Names are matched to the dish catalogue
and converted to grams.

**Files.** `backend/app/kitchen/waste.py`, `tray_scan.py`,
`models/kitchen.py`, migration `a7c3e91f2b10`, `frontend/src/pages/dashboard/WastePage.tsx`.

## 2. Budget-aware menu planner (`/dashboard/menu-planner`)

**What it does.** You set a budget per plate (say ₹50), a diet (veg, Jain, egg,
non-veg) and a nutrition standard (PM POSHAN school norms, or a hostel lunch at
about one third of ICMR-NIN daily needs). It returns a 7-day menu that meets
every rule, either the cheapest or the most nutritious.

**How (one sentence for an interview).** It's an optimisation problem: every
(day, dish) pair is a yes/no variable, each rule is a linear constraint, and a
mixed-integer linear programming solver (SciPy's HiGHS) finds the best valid
combination in about one to three seconds.

```
variables   x[day, dish] ∈ {0, 1}
each day    exactly 1 grain, 1 dal, 1 sabzi, (1 roti), 1–2 sides
            Σ nutrients ≥ target,  energy within range,  Σ cost ≤ budget
each week   same curry ≤ N times, never two days running
objective   maximise nutrition vs targets   (or minimise cost)
```

**When no menu is possible**, it doesn't just fail. It switches off one rule
group at a time to find the blocker ("the budget"), then solves a second problem
(minimise the most expensive day's cost) to report the **lowest budget that
works**: "₹25 is impossible; the minimum is ₹43.45". One click applies it.

**Data.** 32 common Indian dishes with nutrients per 100 g from the Indian Food
Composition Tables (IFCT 2017, ICMR-NIN), standard portions and approximate
2026 institutional cost per kg: `backend/app/kitchen/catalog.py`.

## 3. Cooking forecast (`/dashboard/forecast`)

**What it does.** Predicts how many students will come to the next meal, with a
likely range, and how many kilos of each dish to cook. It compares that with
what the kitchen cooked last time.

**How.** Classical time-series decomposition, no black box:

1. **Weekly pattern**: average plates per weekday ÷ overall average (Sundays ≈ 0.7).
2. **Recent level**: weighted average, where a day 14 days old counts half as much as yesterday.
3. **Trend**: slope over the last four weeks, capped at ±1% a day.
4. **Events**: optional multipliers (exam week, long weekend, festival).
5. **Range**: 80% band from the method's own past errors.
6. **Cook for** the top of the range (80th percentile), × how much students *actually take* of each dish, measured from past logs. Popular rajma gets more, the lauki that comes back on plates gets less.

**Accuracy, measured honestly.** For each of the last 28 days it forecasts
using only the data before that day and compares with what happened. On the
sample data the forecast is off by about 3–4%, versus about 4% for the obvious
guess "same as last week". Across 60 simulated kitchens it beat that guess in 57.

---

## Try it in two minutes

1. Register, open **Food waste**, click **Load sample data** (eight weeks, clearly labelled as sample).
2. Waste page: point at the pot-versus-plate split, the dish ranking, and the iron gap.
3. **Menu planner**: plan at ₹50. Then drag the budget to ₹25 and show it explaining *why* and offering the minimum budget.
4. **Cooking forecast**: tomorrow's headcount, the range, the accuracy card, and kilos per dish.
5. Open **How this works** on any page: every number is explained in plain language.

## Interview questions you should expect

**Why linear programming and not just asking an LLM for a menu?**
An LLM can't guarantee that every day meets the iron target and stays under ₹50.
A solver either proves a menu satisfies every constraint or proves none exists.
The LLM is used where it's strong (reading a tray photo), the solver where
correctness matters.

**Why not a neural network for the forecast?**
Eight weeks of one kitchen's data is about 56 points per meal. A simple,
explainable model that beats the naive baseline is the right tool, and a kitchen
manager can understand why it predicted 384.

**How do you know the forecast is good?**
Walk-forward backtesting: never test on data the model has seen, and always
compare with a baseline.

**What's synthetic?**
The sample kitchen logs (flagged `is_sample` and labelled in the UI). The dish
nutrition values are real IFCT-based approximations; costs are approximate.

**What would you do next?**
Learn event multipliers from history, let the planner use measured plate waste
as a penalty (stop scheduling dishes nobody eats), and a weekly WhatsApp-style
summary for the kitchen head.

## Resume bullets

- Built a **budget-aware menu planner** that formulates weekly meal planning as a mixed-integer linear program (SciPy/HiGHS) over ~200 binary decisions; meets ICMR-NIN/PM POSHAN nutrient targets under a per-plate budget in 1–3 s, and diagnoses infeasible requests by computing the minimum viable budget.
- Designed a **food-waste analytics module** separating over-production from plate waste, quantifying ₹ lost and the nutrient gap between served and eaten food; added an AI tray scan that compares before/after photos with a vision LLM behind a provider-failover layer.
- Implemented a **headcount and cooking-quantity forecast** (weekday seasonality, exponentially weighted level, capped trend) with walk-forward backtesting; ~3–4% average error and better than the naive baseline in 57 of 60 simulated kitchens.
- Shipped end to end: FastAPI + SQLAlchemy/Alembic (PostgreSQL), React/TypeScript dashboards, 20 new pytest tests (79 total), deployed on Render with Neon Postgres.
