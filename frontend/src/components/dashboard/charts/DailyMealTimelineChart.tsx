import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { ChartCard, ChartLegendItem } from "@/components/ui/ChartCard";
import { chartColors } from "@/lib/chartColors";

const toneColor: Record<string, string> = {
  good: chartColors.primary,
  warning: chartColors.amber,
  poor: chartColors.red,
};

const data = [
  { hour: 7.5, location: 1, meal: "Breakfast — Idli & Sambar", compliance: 90, tone: "good" },
  { hour: 8.1, location: 2, meal: "Breakfast — Poha", compliance: 82, tone: "good" },
  { hour: 12.5, location: 1, meal: "Lunch — Veg Thali", compliance: 94, tone: "good" },
  { hour: 12.9, location: 2, meal: "Lunch — Rice & Dal", compliance: 71, tone: "warning" },
  { hour: 13.2, location: 3, meal: "Lunch — Chapati & Sabzi", compliance: 65, tone: "poor" },
  { hour: 16.3, location: 1, meal: "Snacks — Fruit Bowl", compliance: 88, tone: "good" },
  { hour: 19.4, location: 1, meal: "Dinner — Paneer Curry", compliance: 76, tone: "warning" },
  { hour: 19.8, location: 2, meal: "Dinner — Khichdi", compliance: 91, tone: "good" },
];

const locations = ["", "Main Canteen", "Hostel Block A", "Hostel Block C"];

function ChartTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  const h = Math.floor(p.hour);
  const m = Math.round((p.hour - h) * 60);
  const time = `${h % 12 === 0 ? 12 : h % 12}:${m.toString().padStart(2, "0")} ${h < 12 ? "AM" : "PM"}`;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{p.meal}</p>
      <p className="mt-1 text-muted-foreground">
        {time} · {locations[p.location]}
      </p>
      <p className="mt-0.5 text-muted-foreground">
        Compliance: <span className="font-semibold text-foreground">{p.compliance}%</span>
      </p>
    </div>
  );
}

export function DailyMealTimelineChart() {
  return (
    <ChartCard
      title="Daily Meal Timeline"
      description="Meal captures across the day, by location"
      legend={
        <>
          <ChartLegendItem color={toneColor.good} label="Compliant" />
          <ChartLegendItem color={toneColor.warning} label="Borderline" />
          <ChartLegendItem color={toneColor.poor} label="Non-compliant" />
        </>
      }
    >
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 4, right: 12, left: -8, bottom: 0 }}>
            <CartesianGrid stroke={chartColors.grid} />
            <XAxis
              type="number"
              dataKey="hour"
              domain={[6, 22]}
              ticks={[6, 9, 12, 15, 18, 21]}
              tickFormatter={(h) => `${h % 12 === 0 ? 12 : h % 12}${h < 12 ? "AM" : "PM"}`}
              stroke={chartColors.axis}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="number"
              dataKey="location"
              domain={[0, 4]}
              ticks={[1, 2, 3]}
              tickFormatter={(v) => locations[v] ?? ""}
              width={100}
              stroke={chartColors.axis}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<ChartTooltip />} cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={data} fill={chartColors.primary}>
              {data.map((d, i) => (
                <Cell key={i} fill={toneColor[d.tone]} r={7} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
