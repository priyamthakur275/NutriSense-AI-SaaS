import { api } from "@/lib/api";

export type MealType = "breakfast" | "lunch" | "dinner";
export type Diet = "veg" | "jain" | "egg" | "non_veg";

export interface CatalogDish {
  key: string;
  name: string;
  category: "grain" | "bread" | "pulse" | "vegetable" | "side";
  portion_g: number;
  cost_per_portion: number;
  cost_per_kg: number;
  per_portion: Record<string, number>;
  veg: boolean;
  jain_ok: boolean;
}
export interface Preset {
  key: string;
  label: string;
  source: string;
  kcal_min: number;
  kcal_max: number;
  minimums: Record<string, number>;
}
export interface Catalog {
  dishes: CatalogDish[];
  presets: Preset[];
  events: { key: string; label: string; multiplier: number }[];
}

export interface WasteSummary {
  has_data: boolean;
  days: number;
  is_sample?: boolean;
  services?: number;
  plates?: number;
  totals?: {
    prepared_kg: number;
    eaten_kg: number;
    pot_leftover_kg: number;
    plate_waste_kg: number;
    waste_kg: number;
    waste_pct: number;
    cost_wasted: number;
    portions_wasted: number;
    waste_g_per_plate: number;
    monthly_cost_projection: number;
  };
  dishes?: {
    key: string;
    name: string;
    services: number;
    prepared_kg: number;
    pot_leftover_kg: number;
    plate_waste_kg: number;
    waste_pct: number;
    plate_waste_pct: number;
    cost_wasted: number;
    portions_wasted: number;
  }[];
  weeks?: { week_start: string; days_logged: number; waste_pct: number; waste_kg: number; pot_kg_per_day: number; plate_kg_per_day: number; cost_wasted: number }[];
  nutrition?: { nutrient: string; served_per_plate: number; eaten_per_plate: number; lost_pct: number }[];
  insights?: string[];
}

export interface TrayScanReport {
  items: { detected: string; key: string | null; name: string; leftover_pct: number; leftover_g: number | null; confidence: number }[];
  plate_leftover_g: number;
  plate_leftover_pct: number | null;
  notes: string | null;
  provider: string;
}

export interface PlanDish { key: string; name: string; category: string; portion_g: number; cost: number }
export interface PlanDay { day: string; dishes: PlanDish[]; totals: Record<string, number>; cost: number }
export interface PlanResult {
  feasible: boolean;
  days: PlanDay[];
  average_cost: number;
  targets: Record<string, { label: string; unit: string; min: number; max: number | null }>;
  explanation: string[];
  solver: { method: string; variables: number; constraints: number; candidate_dishes: number; solve_ms: number; status: string };
  blockers: string[];
  cheapest_feasible_cost: number | null;
}
export interface PlanRequest {
  preset: string;
  budget_per_plate: number;
  diet: Diet;
  days: number;
  include_bread: boolean;
  max_repeats: number;
  goal: "nutrition" | "cost";
}

export interface ForecastResult {
  has_data: boolean;
  message?: string;
  target_date: string;
  weekday: string;
  event: string;
  event_label: string;
  expected_headcount: number;
  range_low: number;
  range_high: number;
  plan_for: number;
  accuracy_mape_pct: number | null;
  naive_mape_pct: number | null;
  accuracy_note: string | null;
  history_points: number;
  cook: { key: string; name: string; cook_kg: number; per_plate_g: number; standard_portion_g: number; basis: string; usual_kg: number | null; saving_kg: number }[];
  saving_kg: number;
  saving_rs: number;
  history: { date: string; plates: number }[];
  method: string[];
}

export const NUTRIENT_LABEL: Record<string, { label: string; unit: string }> = {
  kcal: { label: "Energy", unit: "kcal" },
  protein_g: { label: "Protein", unit: "g" },
  iron_mg: { label: "Iron", unit: "mg" },
  calcium_mg: { label: "Calcium", unit: "mg" },
  fibre_g: { label: "Fibre", unit: "g" },
};

export const rupees = (n: number, digits = 0) =>
  "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: digits, minimumFractionDigits: digits });

export const kitchenApi = {
  catalog: () => api.get<Catalog>("/kitchen/catalog").then((r) => r.data),
  wasteSummary: (days: number) => api.get<WasteSummary>(`/kitchen/waste/summary?days=${days}`).then((r) => r.data),
  loadSample: () => api.post<{ created: number }>("/kitchen/sample-data").then((r) => r.data),
  clearSample: () => api.delete<{ removed: number }>("/kitchen/sample-data").then((r) => r.data),
  logService: (body: unknown) => api.post("/kitchen/services", body).then((r) => r.data),
  trayScan: (before: File, after: File) => {
    const form = new FormData();
    form.append("before", before);
    form.append("after", after);
    return api
      .post<TrayScanReport>("/kitchen/waste/tray-scan", form, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => r.data);
  },
  plan: (body: PlanRequest) => api.post<PlanResult>("/kitchen/menu-plan", body).then((r) => r.data),
  forecast: (params: { target_date: string; meal_type: MealType; event: string; dishes?: string[] }) => {
    const q = new URLSearchParams({ target_date: params.target_date, meal_type: params.meal_type, event: params.event });
    if (params.dishes?.length) q.set("dishes", params.dishes.join(","));
    return api.get<ForecastResult>(`/kitchen/forecast?${q}`).then((r) => r.data);
  },
};

/** Pulls a readable message out of an API error. */
export function apiError(err: unknown, fallback: string): string {
  const e = err as { response?: { data?: { detail?: unknown; message?: string } } };
  const detail = e?.response?.data?.detail ?? e?.response?.data?.message;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg).replace(/^Value error, /, "");
  return fallback;
}
