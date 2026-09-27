import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AlertCircle, Bot, Zap, FileText, Check, X } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
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
