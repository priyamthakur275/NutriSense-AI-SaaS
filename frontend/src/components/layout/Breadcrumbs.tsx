import { Link, useLocation } from "react-router-dom";
import { ChevronRight, Home } from "lucide-react";

const labelMap: Record<string, string> = {
  dashboard: "Dashboard",
  meals: "Meals",
  compliance: "Compliance",
  attendance: "Attendance",
  recommendations: "Recommendations",
  reports: "Reports",
  settings: "Settings",
};

export function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  if (segments.length <= 1) {
    return (
      <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <Home size={14} />
        <span className="font-medium text-foreground">Overview</span>
      </div>
    );
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground">
      <Link to="/dashboard" className="flex items-center hover:text-foreground">
        <Home size={14} />
      </Link>
      {segments.slice(1).map((segment, i) => {
        const isLast = i === segments.length - 2;
        const path = "/" + segments.slice(0, i + 2).join("/");
        return (
          <span key={path} className="flex items-center gap-1.5">
            <ChevronRight size={13} />
            {isLast ? (
              <span className="font-medium text-foreground">
                {labelMap[segment] ?? segment}
              </span>
            ) : (
              <Link to={path} className="hover:text-foreground">
                {labelMap[segment] ?? segment}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
