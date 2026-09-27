import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { ChartCard } from "@/components/ui/ChartCard";
import { chartColors } from "@/lib/chartColors";

const data = [
  { day: "Mon", protein: 68, carbs: 220, fat: 52 },
  { day: "Tue", protein: 74, carbs: 235, fat: 58 },
  { day: "Wed", protein: 61, carbs: 198, fat: 47 },
  { day: "Thu", protein: 80, carbs: 250, fat: 61 },
  { day: "Fri", protein: 70, carbs: 228, fat: 55 },
  { day: "Sat", protein: 58, carbs: 190, fat: 44 },
  { day: "Sun", protein: 66, carbs: 210, fat: 50 },
];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} className="mt-1 flex items-center gap-1.5 text-muted-foreground">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.fill }} />
          {p.name}: <span className="font-semibold text-foreground">{p.value}g</span>
        </p>
      ))}
    </div>
  );
}

export function WeeklyNutritionChart() {
  return (
    <ChartCard title="Weekly Nutrition" description="Macronutrient totals, last 7 days">
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }} barGap={3}>
            <CartesianGrid stroke={chartColors.grid} vertical={false} />
            <XAxis
              dataKey="day"
              stroke={chartColors.axis}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis stroke={chartColors.axis} fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: "hsl(var(--secondary))" }} />
            <Legend
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            />
            <Bar dataKey="protein" name="Protein" fill={chartColors.primary} radius={[3, 3, 0, 0]} />
            <Bar dataKey="carbs" name="Carbs" fill={chartColors.blue} radius={[3, 3, 0, 0]} />
            <Bar dataKey="fat" name="Fat" fill={chartColors.amber} radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
