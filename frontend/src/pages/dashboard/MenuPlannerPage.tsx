import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/Button";
import { Bar, HowItWorks, PageIntro, Panel, Stat, fieldClass } from "@/components/kitchen/KitchenUI";
import { NUTRIENT_LABEL, apiError, kitchenApi, rupees, type Diet, type PlanRequest, type PlanResult } from "@/lib/kitchen";
import { cn } from "@/lib/utils";

const DIETS: { key: Diet; label: string }[] = [
  { key: "veg", label: "Vegetarian" },
  { key: "egg", label: "Veg + egg" },
  { key: "non_veg", label: "Non-veg" },
  { key: "jain", label: "Jain" },
];

const CATEGORY_DOT: Record<string, string> = {
  grain: "bg-[#E8DFC6]",
  bread: "bg-[#D9A866]",
  pulse: "bg-turmeric",
  vegetable: "bg-primary",
  side: "bg-steel",
};

export default function MenuPlannerPage() {
  const catalog = useQuery({ queryKey: ["kitchen-catalog"], queryFn: kitchenApi.catalog, staleTime: Infinity });
  const [req, setReq] = useState<PlanRequest>({
    preset: "hostel_lunch",
    budget_per_plate: 50,
    diet: "veg",
    days: 7,
    include_bread: true,
    max_repeats: 2,
    goal: "nutrition",
  });
  const [result, setResult] = useState<PlanResult | null>(null);
  const plan = useMutation({
    mutationFn: () => kitchenApi.plan(req),
    onSuccess: setResult,
    onError: (e) => toast.error(apiError(e, "Couldn't plan the menu")),
  });
  const set = <K extends keyof PlanRequest>(k: K, v: PlanRequest[K]) => setReq((r) => ({ ...r, [k]: v }));
  const preset = catalog.data?.presets.find((p) => p.key === req.preset);

  return (
    <div className="flex flex-col gap-6">
      <PageIntro
        title="Menu planner"
        description="Set a budget per plate, a diet and a nutrition standard. The planner picks a week of dishes that meets every rule at the lowest cost or with the most nutrition."
      />

      <Panel>
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
          <label className="text-sm font-medium">
            Nutrition standard
            <select value={req.preset} onChange={(e) => set("preset", e.target.value)} className={`${fieldClass} mt-1.5`}>
              {catalog.data?.presets.map((p) => <option key={p.key} value={p.key}>{p.label}</option>)}
            </select>
            {preset && <span className="mt-1.5 block text-xs font-normal text-muted-foreground">{preset.source}</span>}
          </label>

          <label className="text-sm font-medium">
            Budget per plate: <span className="tabular text-primary">{rupees(req.budget_per_plate)}</span>
            <input
              type="range" min={20} max={90} step={1} value={req.budget_per_plate}
              onChange={(e) => set("budget_per_plate", Number(e.target.value))}
              className="mt-4 w-full accent-[hsl(var(--primary))]"
            />
            <span className="mt-1 flex justify-between text-xs font-normal text-muted-foreground"><span>₹20</span><span>₹90</span></span>
          </label>

          <fieldset className="text-sm font-medium">
            <legend>Diet</legend>
            <div className="mt-1.5 grid grid-cols-2 gap-2">
              {DIETS.map((d) => (
                <button
                  key={d.key} type="button" onClick={() => set("diet", d.key)} aria-pressed={req.diet === d.key}
                  className={cn("h-10 rounded-xl border text-sm", req.diet === d.key ? "border-primary bg-accent font-semibold text-accent-foreground" : "border-border hover:bg-secondary")}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </fieldset>

          <fieldset className="text-sm font-medium">
            <legend>Optimise for</legend>
            <div className="mt-1.5 grid grid-cols-2 gap-2">
              {([["nutrition", "Most nutrition"], ["cost", "Lowest cost"]] as const).map(([k, label]) => (
                <button
                  key={k} type="button" onClick={() => set("goal", k)} aria-pressed={req.goal === k}
                  className={cn("h-10 rounded-xl border text-sm", req.goal === k ? "border-primary bg-accent font-semibold text-accent-foreground" : "border-border hover:bg-secondary")}
                >
                  {label}
                </button>
              ))}
            </div>
          </fieldset>
        </div>

        <div className="mt-5 flex flex-col gap-4 border-t border-border pt-5 md:flex-row md:items-end md:justify-between">
          <div className="flex flex-wrap gap-5 text-sm">
            <label className="font-medium">
              Days
              <select value={req.days} onChange={(e) => set("days", Number(e.target.value))} className={`${fieldClass} mt-1.5 w-28`}>
                {[5, 6, 7].map((d) => <option key={d} value={d}>{d} days</option>)}
              </select>
            </label>
            <label className="font-medium">
              Same curry at most
              <select value={req.max_repeats} onChange={(e) => set("max_repeats", Number(e.target.value))} className={`${fieldClass} mt-1.5 w-36`}>
                {[1, 2, 3].map((d) => <option key={d} value={d}>{d}× a week</option>)}
              </select>
            </label>
            <label className="flex items-center gap-2 self-end pb-3 font-medium">
              <input type="checkbox" checked={req.include_bread} onChange={(e) => set("include_bread", e.target.checked)} className="h-4 w-4 accent-[hsl(var(--primary))]" />
              Serve roti every day
            </label>
          </div>
          <div className="flex flex-col items-start gap-1.5 md:items-end">
            <Button onClick={() => plan.mutate()} loading={plan.isPending} className="h-11 px-6">
              {plan.isPending ? "Solving…" : "Plan the week"}
            </Button>
            {plan.isPending && <span className="text-xs text-muted-foreground">Checking every combination; this takes a few seconds.</span>}
          </div>
        </div>
      </Panel>

      {result && !result.feasible && (
        <Panel className="border-turmeric/50 bg-turmeric/10">
          <h2 className="font-display text-xl font-bold">No menu fits these rules</h2>
          <ul className="mt-3 space-y-2 text-[15px] leading-relaxed">
            {result.explanation.slice(1).map((l) => <li key={l}>{l}</li>)}
          </ul>
          {result.cheapest_feasible_cost && (
            <Button className="mt-4" onClick={() => { set("budget_per_plate", Math.ceil(result.cheapest_feasible_cost!)); toast.message(`Budget set to ${rupees(Math.ceil(result.cheapest_feasible_cost!))}. Plan again.`); }}>
              Use {rupees(Math.ceil(result.cheapest_feasible_cost))} per plate
            </Button>
          )}
          {result.blockers.includes("variety") && req.max_repeats < 3 && (
            <Button variant="outline" className="ml-2 mt-4" onClick={() => set("max_repeats", req.max_repeats + 1)}>
              Allow each curry {req.max_repeats + 1}× a week
            </Button>
          )}
        </Panel>
      )}

      {result?.feasible && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Stat label="Average cost per plate" value={rupees(result.average_cost, 2)} sub={`Budget ${rupees(req.budget_per_plate)}`} tone="good" />
            <Stat label="Weekly food cost per student" value={rupees(result.average_cost * result.days.length)} sub={`${result.days.length} meals`} />
            <Stat label="Solved in" value={result.solver.solve_ms >= 1000 ? `${(result.solver.solve_ms / 1000).toFixed(1)} s` : `${Math.round(result.solver.solve_ms)} ms`} sub={`${result.solver.variables} yes/no choices, ${result.solver.constraints} rules`} />
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {result.days.map((day) => (
              <article key={day.day} className="flex flex-col rounded-2xl border border-border bg-card p-5">
                <div className="flex items-baseline justify-between">
                  <h3 className="font-display text-lg font-bold">{day.day}</h3>
                  <span className="tabular text-sm font-semibold">{rupees(day.cost, 2)}</span>
                </div>
                <ul className="mt-3 space-y-1.5">
                  {day.dishes.map((d) => (
                    <li key={d.key} className="flex items-center gap-2.5 text-[15px]">
                      <span className={cn("h-2.5 w-2.5 flex-shrink-0 rounded-full", CATEGORY_DOT[d.category])} />
                      <span className="flex-1">{d.name}</span>
                      <span className="tabular text-xs text-muted-foreground">{d.portion_g} g</span>
                    </li>
                  ))}
                </ul>
                <dl className="mt-auto grid grid-cols-3 gap-2 border-t border-border pt-3 text-xs">
                  {(["kcal", "protein_g", "iron_mg"] as const).map((n) => (
                    <div key={n}>
                      <dt className="text-muted-foreground">{NUTRIENT_LABEL[n].label}</dt>
                      <dd className="tabular font-semibold">{day.totals[n]} {NUTRIENT_LABEL[n].unit}</dd>
                    </div>
                  ))}
                </dl>
              </article>
            ))}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_1.2fr]">
            <Panel title="Targets met every day" description="Lowest day against the target.">
              <div className="space-y-4">
                {Object.entries(result.targets).map(([n, t]) => {
                  const lowest = Math.min(...result.days.map((d) => d.totals[n]));
                  return (
                    <div key={n}>
                      <div className="mb-1.5 flex justify-between text-sm">
                        <span className="font-medium">{t.label}</span>
                        <span className="tabular text-muted-foreground">
                          lowest <b className="text-foreground">{lowest}</b> / target {t.min}{t.max ? `–${t.max}` : "+"} {t.unit}
                        </span>
                      </div>
                      <Bar pct={Math.min(100, (100 * lowest) / (t.min * 1.6))} />
                    </div>
                  );
                })}
              </div>
            </Panel>
            <Panel title="Why this plan">
              <ul className="space-y-2.5 text-[15px] leading-relaxed">
                {result.explanation.map((l) => <li key={l}>{l}</li>)}
              </ul>
            </Panel>
          </div>
        </>
      )}

      <HowItWorks
        steps={[
          "Every pair of (day, dish) is a yes/no choice. With about 30 vegetarian dishes over 7 days that is roughly 200 choices.",
          "Each rule becomes a linear constraint: one grain, one dal, one sabzi per day; daily nutrients above the target; daily cost under the budget; no curry more than the repeat limit or on two days running.",
          "A mixed-integer linear programming solver (SciPy's HiGHS) searches the combinations and returns the best valid menu, usually in under two seconds.",
          "If no menu is possible, the planner switches off one rule at a time to find the blocker, and solves a second problem to find the smallest budget that would work.",
          "Nutrient values are per standard portion, from the Indian Food Composition Tables (IFCT 2017). School targets are the PM POSHAN norms.",
        ]}
      />
    </div>
  );
}
