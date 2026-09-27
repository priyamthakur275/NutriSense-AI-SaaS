import { Camera, ShieldCheck, Users, Bot, HeartPulse, Target } from "lucide-react";
import { StatCard } from "@/components/ui/StatCard";
import { WelcomeCard } from "@/components/dashboard/WelcomeCard";
import { NutritionSummaryCard } from "@/components/dashboard/NutritionSummaryCard";
import { ScoreCard } from "@/components/dashboard/ScoreCard";
import { RecentMealsCard } from "@/components/dashboard/RecentMealsCard";
import { RecentActivityCard } from "@/components/dashboard/RecentActivityCard";
import { UpcomingAlertsCard } from "@/components/dashboard/UpcomingAlertsCard";
import { QuickActionsCard } from "@/components/dashboard/QuickActionsCard";
import { AIRecommendationCard } from "@/components/dashboard/AIRecommendationCard";
import { SmartInsightsCard } from "@/components/dashboard/SmartInsightsCard";
import { CaloriesTrendChart } from "@/components/dashboard/charts/CaloriesTrendChart";
import { WeeklyNutritionChart } from "@/components/dashboard/charts/WeeklyNutritionChart";
import { MacronutrientBreakdownChart } from "@/components/dashboard/charts/MacronutrientBreakdownChart";
import { ComplianceTrendChart } from "@/components/dashboard/charts/ComplianceTrendChart";
import { DailyMealTimelineChart } from "@/components/dashboard/charts/DailyMealTimelineChart";
import { ProgressIndicatorsCard } from "@/components/dashboard/charts/ProgressIndicatorsCard";

export default function OverviewPage() {
  return (
    <div className="flex flex-col gap-8">
      <WelcomeCard />

      {/* Top-level stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Meals Analyzed Today" value={1284} icon={Camera} trend="up" trendLabel="+4.2%" delay={0} />
        <StatCard label="Compliance Rate" value={92.4} suffix="%" decimals={1} icon={ShieldCheck} trend="up" trendLabel="+1.8%" delay={0.05} />
        <StatCard label="Attendance Logged" value={1190} icon={Users} trend="flat" trendLabel="steady" delay={0.1} />
        <StatCard label="AI Recommendations" value={18} icon={Bot} trend="down" trendLabel="-3" delay={0.15} />
      </div>

      {/* Nutrition + scores */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <NutritionSummaryCard />
        </div>
        <div className="flex flex-col gap-4">
          <ScoreCard
            title="Compliance Score"
            score={92}
            description="Institution-wide average today"
            icon={ShieldCheck}
            status="success"
            statusLabel="On track"
            delay={0.05}
          />
          <ScoreCard
            title="Health Score"
            score={78}
            description="Composite nutrient adequacy index"
            icon={HeartPulse}
            status="warning"
            statusLabel="Needs attention"
            delay={0.1}
          />
        </div>
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-6 lg:col-span-2">
          <AIRecommendationCard />
          <RecentMealsCard />
          <SmartInsightsCard />
        </div>
        <div className="flex flex-col gap-8">
          <QuickActionsCard />
          <ScoreCard
            title="Weekly Goal"
            score={68}
            description="Progress toward this week's nutrition target"
            icon={Target}
            status="warning"
            statusLabel="4 days left"
            delay={0.15}
          />
          <UpcomingAlertsCard />
          <RecentActivityCard />
        </div>
      </div>

      {/* Analytics */}
      <div className="flex flex-col gap-1.5 pt-2">
        <h2 className="text-lg font-semibold tracking-tight">Analytics</h2>
        <p className="text-sm text-muted-foreground">
          Deeper trends across nutrition, compliance, and meal timing.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <CaloriesTrendChart />
        <ComplianceTrendChart />
        <WeeklyNutritionChart />
        <MacronutrientBreakdownChart />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DailyMealTimelineChart />
        </div>
        <ProgressIndicatorsCard />
      </div>
    </div>
  );
}
