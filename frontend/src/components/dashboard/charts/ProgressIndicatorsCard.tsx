import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";

const indicators = [
  { label: "Weekly protein target", value: 82, valueLabel: "82%" },
  { label: "Weekly iron target", value: 58, valueLabel: "58%" },
  { label: "Weekly calcium target", value: 74, valueLabel: "74%" },
  { label: "Attendance-linked meals", value: 96, valueLabel: "96%" },
  { label: "Reports submitted on time", value: 89, valueLabel: "89%" },
];

const toneFor = (v: number) =>
  v >= 80 ? "bg-emerald-500" : v >= 60 ? "bg-amber-500" : "bg-red-500";

export function ProgressIndicatorsCard() {
  return (
    <Card className="p-6">
      <CardHeader className="p-0 pb-5">
        <CardTitle>Progress Indicators</CardTitle>
        <CardDescription>Weekly targets across key metrics</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4 p-0">
        {indicators.map((ind, i) => (
          <ProgressBar
            key={ind.label}
            label={ind.label}
            valueLabel={ind.valueLabel}
            value={ind.value}
            barClassName={toneFor(ind.value)}
            delay={i * 0.06}
          />
        ))}
      </CardContent>
    </Card>
  );
}
