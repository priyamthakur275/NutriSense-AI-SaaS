import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ChartCard } from "@/components/ui/ChartCard";
import { chartColors } from "@/lib/chartColors";

const data = [
  { day: "Mon", calories: 2050, target: 2200 },
  { day: "Tue", calories: 2180, target: 2200 },
  { day: "Wed", calories: 1960, target: 2200 },
  { day: "Thu", calories: 2240, target: 2200 },
  { day: "Fri", calories: 2100, target: 2200 },
  { day: "Sat", calories: 1840, target: 2200 },
  { day: "Sun", calories: 2020, target: 2200 },
];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{label}</p>
      <p className="mt-1 text-muted-foreground">
        <span className="font-semibold text-foreground">{payload[0].value}</span> kcal
      </p>
    </div>
  );
}

export function CaloriesTrendChart() {
  return (
    <ChartCard title="Calories Trend" description="Average daily intake, last 7 days">
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="caloriesFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={chartColors.primary} stopOpacity={0.35} />
                <stop offset="100%" stopColor={chartColors.primary} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke={chartColors.grid} vertical={false} />
            <XAxis
              dataKey="day"
              stroke={chartColors.axis}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis stroke={chartColors.axis} fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: chartColors.grid }} />
            <Area
              type="monotone"
              dataKey="calories"
              stroke={chartColors.primary}
              strokeWidth={2}
              fill="url(#caloriesFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
