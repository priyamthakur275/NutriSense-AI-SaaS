import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import { ChartCard, ChartLegendItem } from "@/components/ui/ChartCard";
import { chartColors } from "@/lib/chartColors";

const data = [
  { week: "W1", compliance: 74 },
  { week: "W2", compliance: 79 },
  { week: "W3", compliance: 77 },
  { week: "W4", compliance: 84 },
  { week: "W5", compliance: 88 },
  { week: "W6", compliance: 86 },
  { week: "W7", compliance: 91 },
  { week: "W8", compliance: 92 },
];

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-medium">{label}</p>
      <p className="mt-1 text-muted-foreground">
        Compliance: <span className="font-semibold text-foreground">{payload[0].value}%</span>
      </p>
    </div>
  );
}

export function ComplianceTrendChart() {
  return (
    <ChartCard
      title="Compliance Trend"
      description="Institution-wide average, last 8 weeks"
      legend={
        <>
          <ChartLegendItem color={chartColors.primary} label="Compliance %" />
          <ChartLegendItem color={chartColors.amber} label="Target threshold (85%)" />
        </>
      }
    >
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid stroke={chartColors.grid} vertical={false} />
            <XAxis
              dataKey="week"
              stroke={chartColors.axis}
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis stroke={chartColors.axis} fontSize={11} tickLine={false} axisLine={false} domain={[60, 100]} />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: chartColors.grid }} />
            <ReferenceLine
              y={85}
              stroke={chartColors.amber}
              strokeDasharray="4 4"
              strokeWidth={1.5}
            />
            <Line
              type="monotone"
              dataKey="compliance"
              stroke={chartColors.primary}
              strokeWidth={2.5}
              dot={{ r: 3, fill: chartColors.primary, strokeWidth: 0 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
