import { motion, useReducedMotion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";

/* One sample tray. Values are per serving and illustrative: they show what a
   scan returns, not a claim about any real institution. */
const detections = [
  { label: "Jeera rice", conf: 96, x: 22, y: 30, w: 168, h: 196 },
  { label: "Dal tadka", conf: 93, x: 206, y: 30, w: 118, h: 96 },
  { label: "Aloo gobi", conf: 89, x: 340, y: 30, w: 118, h: 96 },
  { label: "Roti ×2", conf: 94, x: 206, y: 140, w: 118, h: 86 },
  { label: "Curd", conf: 91, x: 340, y: 140, w: 118, h: 86 },
];

const nutrients = [
  { label: "Energy", value: "642 kcal", pct: 92 },
  { label: "Protein", value: "19 g", pct: 76 },
  { label: "Iron", value: "3.1 mg", pct: 41, low: true },
  { label: "Calcium", value: "212 mg", pct: 62 },
];

const audiences = ["School midday meals", "College hostels", "Hospital kitchens", "Corporate canteens"];

function Tray({ reduce }: { reduce: boolean }) {
  return (
    <svg viewBox="0 0 480 256" className="h-auto w-full" role="img" aria-label="Top-down photo of a steel meal tray with rice, dal, aloo gobi, two rotis and curd, each outlined by the detector">
      <defs>
        <linearGradient id="steel" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#E9EDEA" />
          <stop offset="0.5" stopColor="#C9D0CC" />
          <stop offset="1" stopColor="#E3E8E5" />
        </linearGradient>
        <linearGradient id="well" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#B7BFBA" />
          <stop offset="1" stopColor="#D8DEDA" />
        </linearGradient>
        <pattern id="rice" width="9" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-18)">
          <rect width="9" height="7" fill="#F4EFE2" />
          <ellipse cx="3" cy="2" rx="2.6" ry="0.9" fill="#FFFDF6" />
          <ellipse cx="7" cy="5" rx="2.6" ry="0.9" fill="#E9E1CC" />
          <circle cx="7.5" cy="1.5" r="0.5" fill="#6B4E2E" />
        </pattern>
      </defs>
      {/* tray */}
      <rect x="6" y="14" width="468" height="228" rx="26" fill="url(#steel)" stroke="#AEB6B1" />
      {/* wells */}
      <rect x="22" y="30" width="168" height="196" rx="18" fill="url(#well)" />
      <rect x="28" y="36" width="156" height="184" rx="14" fill="url(#rice)" />
      <rect x="206" y="30" width="118" height="96" rx="16" fill="url(#well)" />
      <ellipse cx="265" cy="78" rx="50" ry="38" fill="#E0A21F" />
      <ellipse cx="258" cy="70" rx="30" ry="16" fill="#EDB84A" opacity="0.7" />
      <circle cx="248" cy="86" r="3" fill="#7A3E12" /><circle cx="281" cy="66" r="2.4" fill="#2F6B2F" /><circle cx="270" cy="92" r="2" fill="#7A3E12" />
      <rect x="340" y="30" width="118" height="96" rx="16" fill="url(#well)" />
      {[[366, 62, 13], [392, 56, 11], [420, 66, 14], [378, 92, 12], [408, 94, 13], [434, 92, 9]].map(([cx, cy, r], i) => (
        <circle key={i} cx={cx} cy={cy} r={r} fill={i % 2 ? "#F2D27A" : "#E8C35A"} stroke="#C99A2E" strokeWidth="1" />
      ))}
      {[[384, 74], [414, 80], [398, 68]].map(([cx, cy], i) => <circle key={i} cx={cx} cy={cy} r="3" fill="#3C7D3C" />)}
      <rect x="206" y="140" width="118" height="86" rx="16" fill="url(#well)" />
      <circle cx="250" cy="183" r="34" fill="#D9A866" stroke="#B9874A" />
      <circle cx="282" cy="186" r="32" fill="#E2B575" stroke="#B9874A" />
      {[[270, 172], [290, 196], [262, 200], [298, 176]].map(([cx, cy], i) => <circle key={i} cx={cx} cy={cy} r="3.2" fill="#8E5A2B" opacity="0.55" />)}
      <rect x="340" y="140" width="118" height="86" rx="16" fill="url(#well)" />
      <ellipse cx="399" cy="183" rx="46" ry="32" fill="#FBFAF5" stroke="#E2E0D6" />
      <ellipse cx="388" cy="176" rx="16" ry="7" fill="#FFFFFF" />

      {/* detections */}
      {detections.map((d, i) => (
        <motion.g
          key={d.label}
          initial={reduce ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: reduce ? 0 : 1.1 + i * 0.22, duration: 0.3 }}
        >
          <rect x={d.x + 2} y={d.y + 2} width={d.w - 4} height={d.h - 4} rx="14" fill="none" stroke="#1E7A4C" strokeWidth="2.5" />
          <rect x={d.x + 8} y={d.y + 8} width={d.label.length * 6.4 + 34} height="19" rx="9.5" fill="#12261D" />
          <text x={d.x + 16} y={d.y + 21.5} fill="#F5F7F2" fontSize="10.5" fontWeight="600" fontFamily="Geist Variable, Geist, sans-serif">
            {d.label}
            <tspan fill="#9FD3B4" dx="5">{d.conf}%</tspan>
          </text>
        </motion.g>
      ))}
    </svg>
  );
}

export function Hero() {
  const navigate = useNavigate();
  const reduce = !!useReducedMotion();

  return (
    <section className="relative overflow-hidden px-5 pb-20 pt-28 md:px-8 md:pb-28 md:pt-36">
      <div className="mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.08fr)] lg:gap-16">
        <div className="max-w-xl">
          <h1 className="font-display text-[2.6rem] font-extrabold leading-[0.98] tracking-[-0.035em] text-foreground sm:text-6xl lg:text-[4.6rem]">
            Know what every plate actually served.
          </h1>
          <p className="mt-7 max-w-[34rem] text-lg leading-relaxed text-muted-foreground">
            Photograph a meal tray. NutriSense identifies each dish, estimates the portion and
            scores the meal against ICMR-NIN and FSSAI guidelines, so your kitchen can close
            nutrient gaps before the next service.
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" onClick={() => navigate("/register")} className="h-12 px-6 text-[15px]">
              Create a free account
            </Button>
            <Button size="lg" variant="outline" onClick={() => navigate("/login")} className="h-12 px-6 text-[15px]">
              Sign in
            </Button>
          </div>
          <div className="mt-12 border-t border-border pt-6">
            <p className="text-sm text-muted-foreground">Built for</p>
            <ul className="mt-3 flex flex-wrap gap-2">
              {audiences.map((a) => (
                <li key={a} className="rounded-full border border-border bg-card px-3.5 py-1.5 text-sm font-medium text-foreground">
                  {a}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Scanner */}
        <div className="relative">
          <div className="rounded-[28px] bg-sidebar p-3 shadow-[0_40px_80px_-40px_rgba(18,38,29,0.55)] ring-1 ring-black/5 dark:ring-white/10 sm:p-4">
            <div className="flex items-center justify-between px-2 pb-3 pt-1 text-[13px] text-sidebar-muted">
              <span className="font-medium text-sidebar-foreground">Lunch, Hostel block C</span>
              <span className="tabular">Tray 214 of 380</span>
            </div>
            <div className="relative overflow-hidden rounded-[20px] bg-[#DDE3DF]">
              <Tray reduce={reduce} />
              {!reduce && (
                <div className="pointer-events-none absolute inset-x-0 top-0 h-full">
                  <div className="animate-tray-scan h-16 w-full bg-gradient-to-b from-transparent via-[#E3A21A]/35 to-transparent">
                    <div className="h-full border-b-2 border-[#E3A21A]" />
                  </div>
                </div>
              )}
            </div>

            <motion.div
              initial={reduce ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: reduce ? 0 : 2.4, duration: 0.4 }}
              className="mt-3 grid gap-3 rounded-[20px] bg-sidebar-active p-4 sm:grid-cols-[1fr_auto]"
            >
              <dl className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
                {nutrients.map((n) => (
                  <div key={n.label}>
                    <dt className="text-xs text-sidebar-muted">{n.label}</dt>
                    <dd className="tabular mt-0.5 text-[15px] font-semibold text-sidebar-foreground">{n.value}</dd>
                    <div className="mt-2 h-1 rounded-full bg-white/10">
                      <div
                        className={n.low ? "h-full rounded-full bg-[#E3A21A]" : "h-full rounded-full bg-[#5DB585]"}
                        style={{ width: `${n.pct}%` }}
                      />
                    </div>
                  </div>
                ))}
              </dl>
              <p className="max-w-[13rem] self-center rounded-xl bg-[#E3A21A]/15 px-3 py-2 text-[13px] leading-snug text-[#F2C866]">
                Iron is at 41% of the meal target. Add greens or jaggery to dinner.
              </p>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
