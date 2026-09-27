import os
import re

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)\frontend\src"

reports_page_tsx = """import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AlertCircle, Calendar, BarChart2, TrendingUp, Download, PieChart as PieChartIcon } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { StatCard } from '@/components/ui/StatCard';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, PieChart, Pie, Cell
} from 'recharts';

export default function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<any>(null);
  const [trend, setTrend] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState('daily');

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        // We catch both endpoints concurrently
        const [summaryRes, trendRes] = await Promise.all([
          api.get(`/ai/reports/summary?period=${period}`),
          api.get(`/ai/reports/nutrition-trend?days=14`)
        ]);
        
        if (isMounted) {
          setSummary(summaryRes.data);
          setTrend(trendRes.data);
          setError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || err.message || 'An error occurred while fetching reports.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    
    fetchData();
    return () => { isMounted = false; };
  }, [period]);

  if (loading && !summary) {
    return (
      <div className="flex flex-col gap-6 p-6 md:p-8 max-w-7xl mx-auto w-full">
        <div className="flex justify-between items-center">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1,2,3,4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-[400px] w-full rounded-xl" />
          <Skeleton className="h-[400px] w-full rounded-xl" />
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="flex flex-col gap-6 p-6 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
        <div className="rounded-xl border border-destructive/50 bg-destructive/10 text-destructive p-6 flex flex-col items-center justify-center min-h-[300px]">
          <AlertCircle className="h-10 w-10 mb-4" />
          <h3 className="text-lg font-semibold">Error Loading Analytics</h3>
          <p className="text-sm mt-2">{error}</p>
          <Button variant="outline" className="mt-4" onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </div>
    );
  }

  // Format trend data for Recharts
  const trendData = trend?.labels?.map((label: string, index: number) => {
    const dataPoint: any = { name: label };
    trend.series.forEach((s: any) => {
      dataPoint[s.label] = s.data[index];
    });
    return dataPoint;
  }) || [];

  const pieData = [
    { name: 'Protein', value: summary?.average_protein || 0 },
    { name: 'Carbs', value: summary?.average_carbs || 0 },
    { name: 'Fat', value: summary?.average_fat || 0 },
  ];
  const COLORS = ['#10b981', '#3b82f6', '#f59e0b'];

  return (
    <div className="flex flex-col gap-8 p-6 md:p-8 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Track daily, weekly, and monthly nutrition and compliance trends.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-secondary/50 p-1 rounded-lg border border-border/50">
            {['daily', 'weekly', 'monthly'].map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${period === p ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
          <Button variant="outline" className="gap-2">
            <Download size={16} /> Export
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          label="Meals Analyzed" 
          value={summary?.meals_analyzed || 0} 
          icon={BarChart2} 
          trend="up" 
          trendLabel="+12%" 
        />
        <StatCard 
          label="Avg Calories" 
          value={summary?.average_calories || 0} 
          decimals={0}
          suffix=" kcal"
          icon={TrendingUp} 
          trend="flat"
          trendLabel="Target: 2200"
        />
        <StatCard 
          label="Compliance Score" 
          value={summary?.average_compliance_score || 0} 
          decimals={1}
          suffix="%"
          icon={Calendar} 
          trend="up"
          trendLabel="On Track"
        />
        <StatCard 
          label="Deficiency Alerts" 
          value={summary?.deficiency_alerts?.length || 0} 
          icon={AlertCircle} 
          trend={summary?.deficiency_alerts?.length > 0 ? "down" : "up"}
          trendLabel={summary?.deficiency_alerts?.length > 0 ? "Needs Review" : "Optimal"}
        />
      </div>

      {summary?.narrative_summary && (
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-6">
            <h3 className="font-semibold text-primary mb-2 flex items-center gap-2">
              <PieChartIcon size={18} /> AI Generated Summary
            </h3>
            <p className="text-sm leading-relaxed text-muted-foreground">
              {summary.narrative_summary}
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 flex flex-col">
          <CardHeader>
            <CardTitle>Nutrition Trends (Last 14 Days)</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-[350px]">
            {trendData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                    itemStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  <Legend />
                  {trend?.series?.map((s: any, i: number) => (
                    <Area 
                      key={s.label}
                      type="monotone" 
                      dataKey={s.label} 
                      stroke={['#10b981', '#3b82f6', '#f59e0b'][i % 3]} 
                      fillOpacity={1} 
                      fill={i === 0 ? "url(#colorCal)" : "none"} 
                    />
                  ))}
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground text-sm">
                No trend data available.
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader>
            <CardTitle>Macronutrient Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-[350px] flex flex-col items-center justify-center">
             {pieData.some(d => d.value > 0) ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px' }}
                    />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
             ) : (
               <div className="text-muted-foreground text-sm">No macronutrient data available.</div>
             )}
          </CardContent>
        </Card>
      </div>

    </div>
  );
}
"""

ai_insights_page_tsx = """import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AlertCircle, Bot, Zap, CheckCircle2, FileText, Check, X } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { Badge } from '@/components/ui/Badge';

export default function AIInsightsPage() {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const response = await api.get('/ai-recommendations');
      setInsights(response.data.items || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load AI Insights.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleReview = async (id: string, status: string) => {
    try {
      await api.post(`/ai-recommendations/${id}/review`, { status });
      // Update local state without full refetch
      setInsights(insights.map(i => i.id === id ? { ...i, status } : i));
    } catch (err: any) {
      console.error(err);
    }
  };

  if (loading && insights.length === 0) {
    return (
      <div className="flex flex-col gap-6 p-6 md:p-8 max-w-7xl mx-auto w-full">
        <Skeleton className="h-10 w-1/4" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-4">
          {[1,2,3,4,5,6].map(i => <Skeleton key={i} className="h-48 w-full rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (error && insights.length === 0) {
    return (
      <div className="flex flex-col gap-6 p-6 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
        <div className="rounded-xl border border-destructive/50 bg-destructive/10 text-destructive p-6 flex flex-col items-center justify-center min-h-[300px]">
          <AlertCircle className="h-10 w-10 mb-4" />
          <h3 className="text-lg font-semibold">Error Loading AI Insights</h3>
          <p className="text-sm mt-2">{error}</p>
          <Button variant="outline" className="mt-4" onClick={fetchInsights}>Try Again</Button>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch(status.toLowerCase()) {
      case 'accepted': return 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20';
      case 'dismissed': return 'bg-red-500/10 text-red-600 border-red-500/20';
      default: return 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20';
    }
  };

  const getInsightIcon = (type: string) => {
    if (type.includes('deficiency') || type.includes('risk')) return <AlertCircle className="text-red-500" size={20} />;
    if (type.includes('improvement')) return <Zap className="text-amber-500" size={20} />;
    return <Bot className="text-primary" size={20} />;
  };

  return (
    <div className="flex flex-col gap-8 p-6 md:p-8 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Insights & Recommendations</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Machine learning driven insights into dietary risks and personalized nutrition plans.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 px-3 py-1 text-sm font-medium">
             {insights.filter(i => i.status.toLowerCase() === 'pending').length} Pending Review
          </Badge>
        </div>
      </div>

      {insights.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-12 text-center min-h-[400px]">
          <Bot className="h-16 w-16 text-muted-foreground/50 mb-4" />
          <h3 className="text-xl font-semibold">No Insights Generated</h3>
          <p className="text-muted-foreground mt-2 max-w-sm">
            AI recommendations will appear here automatically once enough nutritional data is processed by the engine.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {insights.map((insight) => (
            <Card key={insight.id} className="flex flex-col hover:shadow-md transition-shadow relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-1 h-full bg-primary/20" />
              <CardHeader className="pb-3 flex flex-row justify-between items-start space-y-0">
                <div className="flex items-center gap-2">
                  {getInsightIcon(insight.recommendation_type)}
                  <span className="font-semibold text-sm capitalize">{insight.recommendation_type.replace('_', ' ')}</span>
                </div>
                <div className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${getStatusColor(insight.status)}`}>
                  {insight.status.toUpperCase()}
                </div>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <p className="text-sm text-foreground/90 leading-relaxed mb-4 flex-1">
                  {insight.content}
                </p>
                <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <FileText size={14} />
                    <span>Agent: {insight.generated_by_agent}</span>
                  </div>
                  {insight.status.toLowerCase() === 'pending' && (
                    <div className="flex gap-2">
                      <Button size="icon" variant="outline" className="h-8 w-8 text-emerald-500 hover:bg-emerald-50 hover:text-emerald-600 border-emerald-500/30" onClick={() => handleReview(insight.id, 'accepted')}>
                        <Check size={14} />
                      </Button>
                      <Button size="icon" variant="outline" className="h-8 w-8 text-red-500 hover:bg-red-50 hover:text-red-600 border-red-500/30" onClick={() => handleReview(insight.id, 'dismissed')}>
                        <X size={14} />
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
"""

with open(os.path.join(base_dir, "pages/dashboard/ReportsPage.tsx"), "w", encoding="utf-8") as f:
    f.write(reports_page_tsx)

with open(os.path.join(base_dir, "pages/dashboard/AIInsightsPage.tsx"), "w", encoding="utf-8") as f:
    f.write(ai_insights_page_tsx)

print("Analytics and AI Insights updated.")
