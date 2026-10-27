import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bar as RBar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { Camera, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/Button";
import { Bar, HowItWorks, PageIntro, Panel, SampleBanner, Stat, fieldClass } from "@/components/kitchen/KitchenUI";
import { chartColors } from "@/lib/chartColors";
import { NUTRIENT_LABEL, apiError, kitchenApi, rupees, type MealType, type TrayScanReport } from "@/lib/kitchen";

const PERIODS = [14, 28, 56];

export default function WastePage() {
  const qc = useQueryClient();
  const [days, setDays] = useState(28);
  const [showForm, setShowForm] = useState(false);
  const summary = useQuery({ queryKey: ["waste", days], queryFn: () => kitchenApi.wasteSummary(days) });
  const refresh = () => qc.invalidateQueries({ queryKey: ["waste"] });

  const loadSample = useMutation({
    mutationFn: kitchenApi.loadSample,
    onSuccess: (r) => { toast.success(`Loaded ${r.created} sample services`); refresh(); qc.invalidateQueries({ queryKey: ["forecast"] }); },
    onError: (e) => toast.error(apiError(e, "Couldn't load sample data")),
  });
  const clearSample = useMutation({
    mutationFn: kitchenApi.clearSample,
    onSuccess: () => { toast.success("Sample data cleared"); refresh(); qc.invalidateQueries({ queryKey: ["forecast"] }); },
  });

  const s = summary.data;
  const t = s?.totals;

  return (
    <div className="flex flex-col gap-6">
      <PageIntro
        title="Food waste"
        description="What was cooked, what came back in the pot, and what students left on their plates, in kilos, rupees and nutrients."
        actions={
          <>
            <div className="flex rounded-xl border border-border bg-card p-1" role="group" aria-label="Period">
              {PERIODS.map((p) => (
                <button
                  key={p}
                  onClick={() => setDays(p)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium ${days === p ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}
                >
                  {p} days
                </button>
              ))}
            </div>
            <Button onClick={() => setShowForm((v) => !v)}>
              <Plus size={16} /> Log a service
            </Button>
          </>
        }
      />

      {showForm && <LogServiceForm onDone={() => { setShowForm(false); refresh(); }} />}

      {summary.isLoading && <div className="h-64 animate-pulse rounded-2xl bg-secondary/60" />}

      {s && !s.has_data && (
        <Panel>
          <div className="flex flex-col items-start gap-4 md:flex-row md:items-center md:justify-between">
            <div className="max-w-xl">
              <h2 className="font-display text-xl font-bold">No services logged in the last {days} days</h2>
              <p className="mt-1.5 text-muted-foreground">
                After each meal, weigh what was cooked, what was left in the pot and what came back on plates.
                Or load eight weeks of sample data to see what the dashboard finds.
              </p>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => loadSample.mutate()} loading={loadSample.isPending}>Load sample data</Button>
              <Button variant="outline" onClick={() => setShowForm(true)}>Log a service</Button>
            </div>
          </div>
        </Panel>
      )}

      {s?.has_data && t && (
        <>
          {s.is_sample && <SampleBanner onClear={() => clearSample.mutate()} clearing={clearSample.isPending} />}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Stat label="Food wasted" value={`${t.waste_pct}%`} tone="warn" sub={`${t.waste_kg.toLocaleString("en-IN")} kg of ${t.prepared_kg.toLocaleString("en-IN")} kg cooked`} />
            <Stat label="Money lost" value={rupees(t.cost_wasted)} sub={`About ${rupees(t.monthly_cost_projection)} a month at this rate`} />
            <Stat label="Portions thrown away" value={t.portions_wasted.toLocaleString("en-IN")} sub={`Over ${s.services} services, ${s.plates?.toLocaleString("en-IN")} plates`} />
            <Stat label="Wasted per plate" value={`${t.waste_g_per_plate} g`} sub="Pot leftovers plus plate waste" />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
            <Panel title="Where the waste happens" description="Over-production never leaves the pot; plate waste is served but not eaten. Chart: average kilos wasted per day, by week.">
              <div className="flex h-4 overflow-hidden rounded-full">
                <div className="bg-steel" style={{ width: `${(100 * t.pot_leftover_kg) / t.waste_kg}%` }} />
                <div className="bg-turmeric" style={{ width: `${(100 * t.plate_waste_kg) / t.waste_kg}%` }} />
              </div>
              <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-sm">
                <span><span className="mr-2 inline-block h-2.5 w-2.5 rounded-full bg-steel" />Left in pot: <b className="tabular">{t.pot_leftover_kg} kg</b></span>
                <span><span className="mr-2 inline-block h-2.5 w-2.5 rounded-full bg-turmeric" />Left on plates: <b className="tabular">{t.plate_waste_kg} kg</b></span>
              </div>
              <div className="mt-6 h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={s.weeks} margin={{ left: -18, right: 4, top: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                    <XAxis dataKey="week_start" tickFormatter={(v: string) => new Date(v).toLocaleDateString("en-IN", { day: "numeric", month: "short" })} tick={{ fontSize: 12, fill: chartColors.axis }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: chartColors.axis }} axisLine={false} tickLine={false} unit=" kg" width={72} />
                    <Tooltip formatter={(v) => `${v} kg a day`} labelFormatter={(v) => `Week of ${new Date(String(v)).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}`} contentStyle={{ borderRadius: 12, fontSize: 13 }} />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                    <RBar dataKey="pot_kg_per_day" name="Left in pot" stackId="w" fill="#9AA6A0" />
                    <RBar dataKey="plate_kg_per_day" name="Left on plates" stackId="w" fill={chartColors.amber} radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Panel>

            <Panel title="What it means">
              <ul className="space-y-3">
                {s.insights?.map((line) => (
                  <li key={line} className="flex gap-3 text-[15px] leading-relaxed">
                    <span className="mt-2 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary" />
                    {line}
                  </li>
                ))}
              </ul>
            </Panel>
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.35fr_1fr]">
            <Panel title="Dishes ranked by money wasted" description="Waste % is share of what was cooked; plate % is share of what was served.">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[520px] text-sm">
                  <thead>
                    <tr className="text-left text-muted-foreground">
                      <th className="pb-3 font-medium">Dish</th>
                      <th className="pb-3 font-medium">Waste</th>
                      <th className="pb-3 text-right font-medium">On plates</th>
                      <th className="pb-3 text-right font-medium">Lost</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {s.dishes?.slice(0, 10).map((d) => (
                      <tr key={d.key}>
                        <td className="py-2.5 pr-3 font-medium">{d.name}</td>
                        <td className="w-[38%] py-2.5 pr-4">
                          <div className="flex items-center gap-3">
                            <Bar pct={d.waste_pct * 3} tone={d.waste_pct >= 20 ? "warn" : "primary"} />
                            <span className="tabular w-11 text-right">{d.waste_pct}%</span>
                          </div>
                        </td>
                        <td className="tabular py-2.5 text-right">{d.plate_waste_pct}%</td>
                        <td className="tabular py-2.5 text-right font-semibold">{rupees(d.cost_wasted)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>

            <Panel title="Nutrition students actually ate" description="Per plate, averaged over the period.">
              <div className="space-y-4">
                {s.nutrition?.map((n) => {
                  const meta = NUTRIENT_LABEL[n.nutrient];
                  return (
                    <div key={n.nutrient}>
                      <div className="mb-1.5 flex items-baseline justify-between text-sm">
                        <span className="font-medium">{meta.label}</span>
                        <span className="tabular text-muted-foreground">
                          <b className="text-foreground">{n.eaten_per_plate}</b> of {n.served_per_plate} {meta.unit} served
                        </span>
                      </div>
                      <Bar pct={(100 * n.eaten_per_plate) / (n.served_per_plate || 1)} />
                    </div>
                  );
                })}
              </div>
            </Panel>
          </div>
        </>
      )}

      <TrayScanPanel />

      <HowItWorks
        steps={[
          "After each meal the kitchen records three weights per dish: cooked, left in the pot, and scraped off returned plates.",
          "Eaten = cooked − pot leftovers − plate waste. Everything here is arithmetic on those numbers.",
          "Rupees lost use each dish's cost per kilo; portions lost divide wasted kilos by the standard serving.",
          "The nutrition panel multiplies what was served and what was eaten by each dish's nutrients (IFCT 2017), so waste shows up as a nutrition gap too.",
          "The tray scan sends a served photo and a returned photo side by side to a vision model, which estimates how much of each dish came back.",
        ]}
      />
    </div>
  );
}

function TrayScanPanel() {
  const [before, setBefore] = useState<File | null>(null);
  const [after, setAfter] = useState<File | null>(null);
  const [report, setReport] = useState<TrayScanReport | null>(null);
  const scan = useMutation({
    mutationFn: () => kitchenApi.trayScan(before!, after!),
    onSuccess: setReport,
    onError: (e) => {
      const code = (e as { response?: { data?: { error_code?: string } } })?.response?.data?.error_code ?? "";
      toast.error(
        code.startsWith("ai_")
          ? "The AI scan isn't available: the server has no working AI key. You can still log weights with “Log a service”."
          : apiError(e, "Couldn't scan the trays")
      );
    },
  });

  return (
    <Panel
      title="Scan returned trays"
      description="Photograph a tray when it's served and again when it comes back. The AI estimates what was left of each dish."
    >
      <div className="grid gap-4 md:grid-cols-[1fr_1fr_auto] md:items-end">
        {[
          { label: "Served tray", file: before, set: setBefore },
          { label: "Returned tray", file: after, set: setAfter },
        ].map(({ label, file, set }) => (
          <label key={label} className="flex cursor-pointer flex-col gap-1.5 text-sm font-medium">
            {label}
            <span className="flex h-11 items-center gap-2 truncate rounded-xl border border-dashed border-border bg-background px-3 font-normal text-muted-foreground hover:border-primary">
              <Camera size={16} className="flex-shrink-0" />
              <span className="truncate">{file ? file.name : "Choose a photo"}</span>
            </span>
            <input type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={(e) => set(e.target.files?.[0] ?? null)} />
          </label>
        ))}
        <Button disabled={!before || !after} loading={scan.isPending} onClick={() => scan.mutate()} className="h-11">
          Scan trays
        </Button>
      </div>
      {report && (
        <div className="mt-5 rounded-xl bg-secondary/60 p-4">
          <p className="font-medium">
            About {report.plate_leftover_g} g left on this plate
            {report.plate_leftover_pct !== null && ` (${report.plate_leftover_pct}% of what was served)`}.
          </p>
          <ul className="mt-3 grid gap-2 sm:grid-cols-2">
            {report.items.map((i) => (
              <li key={i.detected} className="flex items-center justify-between rounded-lg bg-card px-3 py-2 text-sm">
                <span>{i.name}</span>
                <span className="tabular font-semibold">{i.leftover_pct}% left{i.leftover_g !== null && ` · ${i.leftover_g} g`}</span>
              </li>
            ))}
          </ul>
          {report.notes && <p className="mt-3 text-sm text-muted-foreground">{report.notes}</p>}
        </div>
      )}
    </Panel>
  );
}

interface Row { dish_key: string; prepared_kg: string; pot_leftover_kg: string; plate_waste_kg: string }

function LogServiceForm({ onDone }: { onDone: () => void }) {
  const catalog = useQuery({ queryKey: ["kitchen-catalog"], queryFn: kitchenApi.catalog, staleTime: Infinity });
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [meal, setMeal] = useState<MealType>("lunch");
  const [plates, setPlates] = useState("");
  const [rows, setRows] = useState<Row[]>([{ dish_key: "steamed_rice", prepared_kg: "", pot_leftover_kg: "", plate_waste_kg: "" }]);
  const save = useMutation({
    mutationFn: () =>
      kitchenApi.logService({
        service_date: date,
        meal_type: meal,
        plates_served: Number(plates),
        dishes: rows.map((r) => ({
          dish_key: r.dish_key,
          prepared_kg: Number(r.prepared_kg),
          pot_leftover_kg: Number(r.pot_leftover_kg || 0),
          plate_waste_kg: Number(r.plate_waste_kg || 0),
        })),
      }),
    onSuccess: () => { toast.success("Service logged"); onDone(); },
    onError: (e) => toast.error(apiError(e, "Check the weights and try again")),
  });
  const update = (i: number, patch: Partial<Row>) => setRows((rs) => rs.map((r, j) => (j === i ? { ...r, ...patch } : r)));
  const valid = Number(plates) > 0 && rows.every((r) => Number(r.prepared_kg) > 0);

  return (
    <Panel title="Log a service" description="Weights in kilograms. Leave a field empty if it was zero.">
      <div className="grid gap-4 sm:grid-cols-3">
        <label className="text-sm font-medium">Date<input type="date" value={date} onChange={(e) => setDate(e.target.value)} className={`${fieldClass} mt-1.5`} /></label>
        <label className="text-sm font-medium">Meal
          <select value={meal} onChange={(e) => setMeal(e.target.value as MealType)} className={`${fieldClass} mt-1.5`}>
            <option value="breakfast">Breakfast</option><option value="lunch">Lunch</option><option value="dinner">Dinner</option>
          </select>
        </label>
        <label className="text-sm font-medium">Plates served<input inputMode="numeric" value={plates} onChange={(e) => setPlates(e.target.value)} placeholder="e.g. 380" className={`${fieldClass} mt-1.5`} /></label>
      </div>
      <div className="mt-5 space-y-3">
        <div className="hidden grid-cols-[1.6fr_1fr_1fr_1fr_auto] gap-3 text-sm text-muted-foreground sm:grid">
          <span>Dish</span><span>Cooked (kg)</span><span>Left in pot (kg)</span><span>Left on plates (kg)</span><span className="w-10" />
        </div>
        {rows.map((r, i) => (
          <div key={i} className="grid grid-cols-2 gap-3 sm:grid-cols-[1.6fr_1fr_1fr_1fr_auto]">
            <select aria-label="Dish" value={r.dish_key} onChange={(e) => update(i, { dish_key: e.target.value })} className={`${fieldClass} col-span-2 sm:col-span-1`}>
              {catalog.data?.dishes.map((d) => <option key={d.key} value={d.key}>{d.name}</option>)}
            </select>
            <input aria-label="Cooked kg" inputMode="decimal" value={r.prepared_kg} onChange={(e) => update(i, { prepared_kg: e.target.value })} placeholder="Cooked" className={fieldClass} />
            <input aria-label="Left in pot kg" inputMode="decimal" value={r.pot_leftover_kg} onChange={(e) => update(i, { pot_leftover_kg: e.target.value })} placeholder="Pot" className={fieldClass} />
            <input aria-label="Left on plates kg" inputMode="decimal" value={r.plate_waste_kg} onChange={(e) => update(i, { plate_waste_kg: e.target.value })} placeholder="Plates" className={fieldClass} />
            <button aria-label="Remove dish" disabled={rows.length === 1} onClick={() => setRows((rs) => rs.filter((_, j) => j !== i))} className="flex h-11 w-10 items-center justify-center rounded-xl text-muted-foreground hover:bg-secondary disabled:opacity-30">
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
      <div className="mt-5 flex flex-wrap justify-between gap-3">
        <Button variant="outline" onClick={() => setRows((rs) => [...rs, { dish_key: "dal_tadka", prepared_kg: "", pot_leftover_kg: "", plate_waste_kg: "" }])}>
          <Plus size={16} /> Add dish
        </Button>
        <Button disabled={!valid} loading={save.isPending} onClick={() => save.mutate()}>Save service</Button>
      </div>
    </Panel>
  );
}
