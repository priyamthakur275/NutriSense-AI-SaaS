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

sidebar_path = os.path.join(base_dir, "components/layout/MobileNav.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    sidebar = f.read()

sidebar_nav_items = "const navItems = [\n"
for p in pages:
    end_str = ", end: true" if p['path'] == "" else ""
    sidebar_nav_items += f"  {{ label: \"{p['label']}\", to: \"/dashboard{'/' + p['path'] if p['path'] else ''}\", icon: {p['icon']}{end_str} }},\n"
sidebar_nav_items += "];"

sidebar = re.sub(r"const navItems = \[[\s\S]*?\];", sidebar_nav_items, sidebar)

icons_needed = set(p['icon'] for p in pages)
icons_needed.update(["X", "LogOut", "Leaf"])
icons_str = "import {\n  " + ",\n  ".join(icons_needed) + ",\n} from \"lucide-react\";"
sidebar = re.sub(r"import \{[\s\S]*?\} from \"lucide-react\";", icons_str, sidebar)

with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(sidebar)

print("MobileNav modified successfully.")
