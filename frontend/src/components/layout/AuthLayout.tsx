import { Link } from "react-router-dom";
import { Leaf } from "lucide-react";

interface AuthLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

const facts = [
  ["Standards checked", "ICMR-NIN, FSSAI, WHO"],
  ["Who signs in", "Students, staff, admins"],
  ["Works on", "Phone, tablet, laptop"],
];

export function AuthLayout({ title, description, children, footer }: AuthLayoutProps) {
  return (
    <div className="grid min-h-screen bg-background lg:grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)]">
      {/* Brand panel */}
      <aside className="relative hidden flex-col justify-between overflow-hidden bg-sidebar p-12 text-[#F5F7F2] lg:flex">
        <Link to="/" className="flex items-center gap-2.5 text-lg font-semibold">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#E3A21A] text-[#12261D]">
            <Leaf size={18} />
          </span>
          NutriSense AI
        </Link>

        <div className="max-w-md">
          <p className="font-display text-[2.6rem] font-extrabold leading-[1.02] tracking-[-0.03em]">
            Every tray, scored before the next meal is planned.
          </p>
          <dl className="mt-10 divide-y divide-white/10 border-y border-white/10">
            {facts.map(([k, v]) => (
              <div key={k} className="flex items-baseline justify-between gap-6 py-4">
                <dt className="text-sidebar-muted">{k}</dt>
                <dd className="text-right font-semibold">{v}</dd>
              </div>
            ))}
          </dl>
        </div>

        <p className="text-sm text-sidebar-muted">Nutrition monitoring for schools, hostels, hospitals and canteens.</p>

        {/* Steel tray silhouette */}
        <svg aria-hidden viewBox="0 0 200 120" className="pointer-events-none absolute -bottom-16 -right-28 w-[28rem] opacity-[0.07]">
          <rect x="2" y="2" width="196" height="116" rx="16" fill="none" stroke="#F5F7F2" strokeWidth="2" />
          <rect x="10" y="10" width="70" height="100" rx="10" fill="none" stroke="#F5F7F2" strokeWidth="2" />
          <rect x="88" y="10" width="48" height="46" rx="10" fill="none" stroke="#F5F7F2" strokeWidth="2" />
          <rect x="142" y="10" width="48" height="46" rx="10" fill="none" stroke="#F5F7F2" strokeWidth="2" />
          <rect x="88" y="64" width="48" height="46" rx="10" fill="none" stroke="#F5F7F2" strokeWidth="2" />
          <rect x="142" y="64" width="48" height="46" rx="10" fill="none" stroke="#F5F7F2" strokeWidth="2" />
        </svg>
      </aside>

      {/* Form */}
      <main className="flex items-center justify-center px-5 py-12 sm:px-10">
        <div className="w-full max-w-[26rem]">
          <Link to="/" className="mb-10 flex items-center gap-2.5 text-lg font-semibold lg:hidden">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <Leaf size={18} />
            </span>
            NutriSense AI
          </Link>
          <h1 className="font-display text-[2rem] font-bold leading-tight tracking-[-0.03em]">{title}</h1>
          {description && <p className="mt-2 text-muted-foreground">{description}</p>}
          <div className="mt-8">{children}</div>
          {footer && <div className="mt-8 text-sm text-muted-foreground">{footer}</div>}
        </div>
      </main>
    </div>
  );
}
