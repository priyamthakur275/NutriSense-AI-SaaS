/**
 * Centralized chart palette. Recharts renders raw SVG attributes, so we use
 * fixed hex values (matched to the primary emerald theme) rather than CSS
 * custom properties, which aren't reliably resolved in every SVG context.
 */
export const chartColors = {
  primary: "#10b981",
  primaryLight: "#6ee7b7",
  primaryMuted: "#a7f3d0",
  amber: "#f59e0b",
  red: "#ef4444",
  blue: "#3b82f6",
  violet: "#8b5cf6",
  grid: "hsl(var(--border))",
  axis: "hsl(var(--muted-foreground))",
};

export const macronutrientColors = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6"];
