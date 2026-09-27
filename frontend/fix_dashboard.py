import os
import re

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)\frontend\src"

pages = [
    {"name": "Overview", "path": "", "icon": "LayoutDashboard", "label": "Dashboard", "api_path": "/health"},
    {"name": "Students", "path": "students", "icon": "Users", "label": "Students", "api_path": "/students"},
    {"name": "Meals", "path": "meals", "icon": "Camera", "label": "Meals", "api_path": "/meals"},
    {"name": "Nutrition", "path": "nutrition", "icon": "Leaf", "label": "Nutrition", "api_path": "/nutrition-records"},
    {"name": "AIInsights", "path": "ai-insights", "icon": "Bot", "label": "AI Insights", "api_path": "/ai-recommendations"},
    {"name": "Compliance", "path": "compliance", "icon": "ShieldCheck", "label": "Compliance", "api_path": "/compliance-reports"},
    {"name": "Reports", "path": "reports", "icon": "FileBarChart", "label": "Reports", "api_path": "/reports"},
    {"name": "Notifications", "path": "notifications", "icon": "Bell", "label": "Notifications", "api_path": "/notifications"},
    {"name": "Settings", "path": "settings", "icon": "Settings", "label": "Settings", "api_path": "/user-settings"},
    {"name": "Profile", "path": "profile", "icon": "User", "label": "Profile", "api_path": "/users/me"},
]

page_template = """import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

export default function __NAME__Page() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.get('__API_PATH__');
        if (isMounted) {
          setData(response.data);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || err.message || 'An error occurred while fetching data.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    
    fetchData();
    return () => { isMounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <div className="h-8 w-1/4 animate-pulse rounded-md bg-secondary/40" />
        <div className="h-4 w-1/3 animate-pulse rounded-md bg-secondary/40" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mt-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 w-full animate-pulse rounded-xl bg-secondary/40" />
          ))}
        </div>
        <div className="h-64 w-full animate-pulse rounded-xl bg-secondary/40 mt-4" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col gap-6 p-6 animate-in fade-in duration-500">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">__LABEL__</h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2 mt-2">
            <span>Dashboard</span>
            <span>/</span>
            <span className="text-foreground">__LABEL__</span>
          </p>
        </div>
        <div className="rounded-xl border border-destructive/50 bg-destructive/10 text-destructive p-6 flex flex-col items-center justify-center min-h-[300px]">
          <AlertCircle className="h-10 w-10 mb-4" />
          <h3 className="text-lg font-semibold">Error Loading __LABEL__</h3>
          <p className="text-sm mt-2">{error}</p>
        </div>
      </div>
    );
  }

  const hasData = data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0);

  return (
    <div className="flex flex-col gap-6 p-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">__LABEL__</h1>
        <p className="text-muted-foreground text-sm flex items-center gap-2 mt-2">
          <span>Dashboard</span>
          <span>/</span>
          <span className="text-foreground">__LABEL__</span>
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
          <h3 className="font-semibold leading-none tracking-tight">Total Records</h3>
          <p className="text-2xl font-bold mt-2">{Array.isArray(data) ? data.length : (data ? 1 : 0)}</p>
        </div>
        <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
          <h3 className="font-semibold leading-none tracking-tight">Status</h3>
          <p className="text-2xl font-bold mt-2 text-green-600">Active</p>
        </div>
        <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
          <h3 className="font-semibold leading-none tracking-tight">Last Updated</h3>
          <p className="text-sm font-medium mt-3">Just now</p>
        </div>
        <div className="rounded-xl border bg-card text-card-foreground shadow p-6">
          <h3 className="font-semibold leading-none tracking-tight">API Connection</h3>
          <p className="text-sm font-medium mt-3 text-green-600">Connected</p>
        </div>
      </div>

      <div className="rounded-xl border bg-card text-card-foreground shadow min-h-[300px] flex items-center justify-center p-6">
        {!hasData ? (
          <div className="text-center max-w-sm">
            <h3 className="text-lg font-semibold">No data available</h3>
            <p className="text-sm text-muted-foreground mt-2">There are currently no __LABEL_LOWER__ records to display. Check back later or create a new record.</p>
          </div>
        ) : (
          <div className="w-full h-full flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Recent __LABEL__ Data</h3>
            <div className="bg-secondary/30 rounded-lg p-4 overflow-auto max-h-[400px]">
              <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
"""

for p in pages:
    if p["name"] == "Overview":
        continue

    content = page_template.replace("__NAME__", p["name"])
    content = content.replace("__LABEL__", p["label"])
    content = content.replace("__LABEL_LOWER__", p["label"].lower())
    content = content.replace("__API_PATH__", p["api_path"])
    
    file_path = os.path.join(base_dir, f"pages/dashboard/{p['name']}Page.tsx")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# update App.tsx
app_tsx_path = os.path.join(base_dir, "App.tsx")
with open(app_tsx_path, "r", encoding="utf-8") as f:
    app_tsx = f.read()

imports = ["const OverviewPage = lazy(() => import('@/pages/dashboard/OverviewPage'));"]
routes = []
for p in pages:
    if p['name'] != "Overview":
        imports.append(f"const {p['name']}Page = lazy(() => import('@/pages/dashboard/{p['name']}Page'));")
    
    if p['path'] == "":
        routes.append(f"""              <Route index element={{<Suspense fallback={{<DashboardPageFallback />}}><OverviewPage /></Suspense>}} />""")
    else:
        routes.append(f"""              <Route path="{p['path']}" element={{<Suspense fallback={{<DashboardPageFallback />}}><{p['name']}Page /></Suspense>}} />""")

imports_str = "\n".join(imports)
routes_str = "\n".join(routes)

app_tsx = re.sub(r"const OverviewPage = lazy\(\(\) => import\('@/pages/dashboard/OverviewPage'\)\);", imports_str, app_tsx)

routes_pattern = r"(<Route path=\"/dashboard\" element=\{<DashboardLayout />\}>\s*)([\s\S]*?)(\s*</Route>)"
app_tsx = re.sub(routes_pattern, r"\1" + routes_str + r"\3", app_tsx)

with open(app_tsx_path, "w", encoding="utf-8") as f:
    f.write(app_tsx)

# update Sidebar.tsx
sidebar_path = os.path.join(base_dir, "components/layout/Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    sidebar = f.read()

sidebar_nav_items = "const navItems = [\n"
for p in pages:
    end_str = ", end: true" if p['path'] == "" else ""
    sidebar_nav_items += f"  {{ label: \"{p['label']}\", to: \"/dashboard{'/' + p['path'] if p['path'] else ''}\", icon: {p['icon']}{end_str} }},\n"
sidebar_nav_items += "];"

sidebar = re.sub(r"const navItems = \[[\s\S]*?\];", sidebar_nav_items, sidebar)

icons_needed = set(p['icon'] for p in pages)
icons_needed.update(["ChevronsLeft", "ChevronsRight", "Leaf"])
icons_str = "import {\n  " + ",\n  ".join(icons_needed) + ",\n} from \"lucide-react\";"
sidebar = re.sub(r"import \{[\s\S]*?\} from \"lucide-react\";", icons_str, sidebar)

with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(sidebar)

print("Files modified successfully.")
