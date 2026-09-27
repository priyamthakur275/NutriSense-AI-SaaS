import os
import re

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)\frontend\src"

# 1. Update Card.tsx for better styling (base level)
card_path = os.path.join(base_dir, "components/ui/Card.tsx")
with open(card_path, "r", encoding="utf-8") as f:
    card_content = f.read()

card_content = card_content.replace(
    '"rounded-xl border border-border bg-card text-card-foreground shadow-sm",',
    '"rounded-xl border border-border/60 bg-card text-card-foreground shadow-sm transition-all duration-300 hover:shadow-md",\n      "backdrop-blur-sm bg-card/95",'
)
with open(card_path, "w", encoding="utf-8") as f:
    f.write(card_content)

# 2. Update StatCard.tsx for hover animation and loading skeleton
statcard_path = os.path.join(base_dir, "components/ui/StatCard.tsx")
with open(statcard_path, "r", encoding="utf-8") as f:
    statcard_content = f.read()

statcard_content = statcard_content.replace(
    '<Card className={cn("p-5", className)}>',
    '<Card className={cn("p-5 relative overflow-hidden group hover:-translate-y-1 hover:shadow-lg transition-all duration-300", className)}>\n        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />'
)
with open(statcard_path, "w", encoding="utf-8") as f:
    f.write(statcard_content)

# 3. Create Table.tsx in components/ui
table_tsx = """import * as React from "react"
import { cn } from "@/lib/utils"

const Table = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(
  ({ className, ...props }, ref) => (
    <div className="relative w-full overflow-auto rounded-lg border border-border shadow-sm">
      <table
        ref={ref}
        className={cn("w-full caption-bottom text-sm", className)}
        {...props}
      />
    </div>
  )
)
Table.displayName = "Table"

const TableHeader = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <thead ref={ref} className={cn("[&_tr]:border-b bg-muted/50 sticky top-0 z-10", className)} {...props} />
  )
)
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
  ({ className, ...props }, ref) => (
    <tbody ref={ref} className={cn("[&_tr:last-child]:border-0", className)} {...props} />
  )
)
TableBody.displayName = "TableBody"

const TableRow = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
  ({ className, ...props }, ref) => (
    <tr
      ref={ref}
      className={cn(
        "border-b border-border transition-colors hover:bg-muted/80 data-[state=selected]:bg-muted odd:bg-card even:bg-muted/20",
        className
      )}
      {...props}
    />
  )
)
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<HTMLTableCellElement, React.ThHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <th
      ref={ref}
      className={cn(
        "h-12 px-4 text-left align-middle font-semibold text-muted-foreground [&:has([role=checkbox])]:pr-0",
        className
      )}
      {...props}
    />
  )
)
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<HTMLTableCellElement, React.TdHTMLAttributes<HTMLTableCellElement>>(
  ({ className, ...props }, ref) => (
    <td ref={ref} className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)} {...props} />
  )
)
TableCell.displayName = "TableCell"

export {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
}
"""
table_path = os.path.join(base_dir, "components/ui/Table.tsx")
with open(table_path, "w", encoding="utf-8") as f:
    f.write(table_tsx)

# 4. Update DashboardLayout.tsx for better spacing and visual hierarchy
layout_path = os.path.join(base_dir, "components/layout/DashboardLayout.tsx")
with open(layout_path, "r", encoding="utf-8") as f:
    layout_content = f.read()

layout_content = layout_content.replace(
    'className="flex-1 overflow-y-auto bg-secondary/20 p-4 md:p-6"',
    'className="flex-1 overflow-y-auto bg-secondary/30 p-6 md:p-8 lg:p-10"'
)
layout_content = layout_content.replace(
    '<PageTransition />',
    '<div className="mx-auto max-w-7xl">\n            <PageTransition />\n          </div>'
)
with open(layout_path, "w", encoding="utf-8") as f:
    f.write(layout_content)

# 5. Update OverviewPage.tsx to have gap-8 instead of gap-6
overview_path = os.path.join(base_dir, "pages/dashboard/OverviewPage.tsx")
with open(overview_path, "r", encoding="utf-8") as f:
    overview = f.read()

overview = overview.replace('className="flex flex-col gap-6"', 'className="flex flex-col gap-8"')
with open(overview_path, "w", encoding="utf-8") as f:
    f.write(overview)

# 6. Enhance Button.tsx
button_path = os.path.join(base_dir, "components/ui/Button.tsx")
if os.path.exists(button_path):
    with open(button_path, "r", encoding="utf-8") as f:
        button = f.read()
    button = button.replace(
        "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
        "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 transition-all active:scale-[0.98]"
    )
    with open(button_path, "w", encoding="utf-8") as f:
        f.write(button)

print("UI enhancements applied.")
