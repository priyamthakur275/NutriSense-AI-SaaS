import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { toast } from "sonner";
import { Button } from "@/components/ui/Button";
import { HowItWorks, PageIntro, Panel, Stat, fieldClass } from "@/components/kitchen/KitchenUI";
import { chartColors } from "@/lib/chartColors";
import { apiError, kitchenApi, rupees, type MealType } from "@/lib/kitchen";

function tomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

export default function ForecastPage() {
  const qc = useQueryClient();
  const catalog = useQuery({ queryKey: ["kitchen-catalog"], queryFn: kitchenApi.catalog, staleTime: Infinity });
  const [date, setDate] = useState(tomorrow());
  const [meal, setMeal] = useState<MealType>("lunch");
  const [event, setEvent] = useState("none");
  const fc = useQuery({
    queryKey: ["forecast", date, meal, event],
    queryFn: () => kitchenApi.forecast({ target_date: date, meal_type: meal, event }),
  });
  const loadSample = useMutation({
    mutationFn: kitchenApi.loadSample,
    onSuccess: () => { toast.success("Sample data loaded"); qc.invalidateQueries({ queryKey: ["forecast"] }); qc.invalidateQueries({ queryKey: ["waste"] }); },
    onError: (e) => toast.error(apiError(e, "Couldn't load sample data")),
  });
  const f = fc.data;

  const chartData = f?.has_data
    ? [...f.history.map((h) => ({ date: h.date, plates: h.plates })), { date: f.target_date, forecast: f.expected_headcount, plates: undefined as number | undefined }]
    : [];

  return (
    <div className="flex flex-col gap-6">
      <PageIntro
        title="Cooking forecast"
        description="How many students to expect at the next meal, and how many kilos of each dish to cook, based on the last eight weeks."
      />

      <Panel>
        <div className="grid gap-4 sm:grid-cols-3">
          <label className="text-sm font-medium">Date<input type="date" value={date} onChange={(e) => setDate(e.target.value)} className={`${fieldClass} mt-1.5`} /></label>
          <label className="text-sm font-medium">Meal
            <select value={meal} onChange={(e) => setMeal(e.target.value as MealType)} className={`${fieldClass} mt-1.5`}>
              <option value="breakfast">Breakfast</option><option value="lunch">Lunch</option><option value="dinner">Dinner</option>
            </select>
          </label>
          <label className="text-sm font-medium">Anything unusual?
            <select value={event} onChange={(e) => setEvent(e.target.value)} className={`${fieldClass} mt-1.5`}>
              {catalog.data?.events.map((ev) => (
                <option key={ev.key} value={ev.key}>{ev.label}{ev.multiplier !== 1 ? ` (×${ev.multiplier})` : ""}</option>
              ))}
            </select>
          </label>
        </div>
      </Panel>

      {fc.isLoading && <div className="h-64 animate-pulse rounded-2xl bg-secondary/60" />}

      {f && !f.has_data && (
        <Panel>
          <div className="flex flex-col items-start gap-4 md:flex-row md:items-center md:justify-between">
            <div className="max-w-xl">
              <h2 className="font-display text-xl font-bold">Not enough history yet</h2>
              <p className="mt-1.5 text-muted-foreground">{f.message}</p>
            </div>
            <Button onClick={() => loadSample.mutate()} loading={loadSample.isPending}>Load sample data</Button>
          </div>
        </Panel>
      )}

      {f?.has_data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Stat label={`Expected on ${f.weekday}`} value={f.expected_headcount} sub={`Likely between ${f.range_low} and ${f.range_high}`} tone="good" />
            <Stat label="Cook for" value={f.plan_for} sub="Top of the likely range, so you rarely run out" />
            <Stat
              label="Average forecast error"
              value={f.accuracy_mape_pct !== null ? `${f.accuracy_mape_pct}%` : "n/a"}
              sub={f.naive_mape_pct !== null ? `Guessing “same as last week” was off by ${f.naive_mape_pct}%` : "Replayed on recent days"}
            />
            <Stat label="Less food cooked than last time" value={`${f.saving_kg} kg`} sub={f.saving_rs > 0 ? `About ${rupees(f.saving_rs)} saved this meal` : "Already cooking close to need"} />
          </div>

          <div className="grid gap-6 xl:grid-cols-[1.1fr_1fr]">
            <Panel title="What to cook" description="Kilos per dish, from how much students actually take of each dish.">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[460px] text-sm">
                  <thead>
                    <tr className="text-left text-muted-foreground">
                      <th className="pb-3 font-medium">Dish</th>
                      <th className="pb-3 text-right font-medium">Cook</th>
                      <th className="pb-3 text-right font-medium">Last time</th>
                      <th className="pb-3 text-right font-medium">Per plate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {f.cook.map((c) => (
                      <tr key={c.key}>
                        <td className="py-3 pr-3 font-medium">{c.name}</td>
                        <td className="tabular py-3 text-right font-display text-base font-bold">{c.cook_kg} kg</td>
                        <td className="tabular py-3 text-right text-muted-foreground">{c.usual_kg !== null ? `${c.usual_kg} kg` : "–"}</td>
                        <td className="tabular py-3 text-right">
                          {c.per_plate_g} g
                          {c.basis === "measured" && c.per_plate_g !== c.standard_portion_g && (
                            <span className={`ml-1.5 text-xs ${c.per_plate_g < c.standard_portion_g ? "text-amber-700 dark:text-amber-400" : "text-primary"}`}>
                              {c.per_plate_g > c.standard_portion_g ? "+" : ""}{c.per_plate_g - c.standard_portion_g}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="mt-3 text-xs text-muted-foreground">Per plate is what students actually took on average; the small number is the difference from the standard portion.</p>
            </Panel>

            <Panel title="Plates served, last four weeks" description={f.accuracy_note ?? undefined}>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ left: -18, right: 8, top: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} vertical={false} />
                    <XAxis dataKey="date" tickFormatter={(v: string) => new Date(v).toLocaleDateString("en-IN", { day: "numeric", month: "short" })} tick={{ fontSize: 11, fill: chartColors.axis }} axisLine={false} tickLine={false} minTickGap={24} />
                    <YAxis tick={{ fontSize: 12, fill: chartColors.axis }} axisLine={false} tickLine={false} width={48} domain={["dataMin - 30", "dataMax + 30"]} />
                    <Tooltip labelFormatter={(v) => new Date(String(v)).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short" })} contentStyle={{ borderRadius: 12, fontSize: 13 }} />
                    <ReferenceLine y={f.plan_for} stroke={chartColors.amber} strokeDasharray="4 4" />
                    <Line type="monotone" dataKey="plates" name="Plates served" stroke={chartColors.primary} strokeWidth={2} dot={{ r: 2.5 }} connectNulls={false} />
                    <Line dataKey="forecast" name="Forecast" stroke={chartColors.amber} strokeWidth={0} dot={{ r: 6, fill: chartColors.amber }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">Yellow dot: forecast for {f.weekday}. Dashed line: the headcount to cook for.</p>
            </Panel>
          </div>

          {f.event !== "none" && (
            <p className="rounded-xl bg-secondary/70 px-4 py-3 text-sm">Adjusted for: {f.event_label}.</p>
          )}
        </>
      )}

      <HowItWorks steps={f?.has_data ? f.method : [
        "Weekly pattern: average plates on each weekday compared with the overall average.",
        "Recent level and trend from the last few weeks, with newer days counting more.",
        "Range from how wrong the method was when replayed on recent days.",
        "Cook quantities from how much students actually take of each dish.",
      ]}>
        <p className="mt-4 text-sm text-muted-foreground">
          Accuracy is measured honestly: for each of the last 28 days, the forecast is made using only the data before that day, then compared with what happened.
        </p>
      </HowItWorks>
    </div>
  );
}
