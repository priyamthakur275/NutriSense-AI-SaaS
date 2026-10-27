/**
 * Centralized chart palette. Recharts renders raw SVG attributes, so we use
 * fixed hex values (matched to the primary emerald theme) rather than CSS
 * custom properties, which aren't reliably resolved in every SVG context.
 */
export const chartColors = {
  primary: "#1E7A4C",
  primaryLight: "#5DB585",
  primaryMuted: "#B9DFC8",
  amber: "#E3A21A",
  red: "#C2452D",
  blue: "#3b82f6",
  violet: "#8b5cf6",
  grid: "hsl(var(--border))",
  axis: "hsl(var(--muted-foreground))",
};

export const macronutrientColors = ["#1E7A4C", "#3E7CB1", "#E3A21A", "#8A6FB8"];
