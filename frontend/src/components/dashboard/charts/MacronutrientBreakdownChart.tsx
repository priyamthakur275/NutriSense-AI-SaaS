import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { ChartCard, ChartLegendItem } from "@/components/ui/ChartCard";
import { macronutrientColors } from "@/lib/chartColors";

const data = [
  { name: "Carbs", value: 45 },
  { name: "Protein", value: 25 },
  { name: "Fat", value: 20 },
  { name: "Fiber", value: 10 },
];

function ChartTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="flex items-center gap-1.5 font-medium">
        <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.payload.fill }} />
        {item.name}
      </p>
      <p className="mt-1 text-muted-foreground">
        <span className="font-semibold text-foreground">{item.value}%</span> of daily intake
      </p>
    </div>
  );
}

export function MacronutrientBreakdownChart() {
  return (
    <ChartCard
      title="Macronutrient Breakdown"
      description="Share of today's total intake"
      legend={data.map((d, i) => (
        <ChartLegendItem key={d.name} color={macronutrientColors[i]} label={`${d.name} (${d.value}%)`} />
      ))}
    >
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={78}
              paddingAngle={3}
              strokeWidth={0}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={macronutrientColors[i % macronutrientColors.length]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
