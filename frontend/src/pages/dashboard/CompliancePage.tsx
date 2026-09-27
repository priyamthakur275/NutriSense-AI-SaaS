import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

export default function CompliancePage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/compliance-reports');
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
          <h1 className="text-3xl font-bold tracking-tight">Compliance</h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2 mt-2">
            <span>Dashboard</span>
            <span>/</span>
            <span className="text-foreground">Compliance</span>
          </p>
        </div>
        <div className="rounded-xl border border-destructive/50 bg-destructive/10 text-destructive p-6 flex flex-col items-center justify-center min-h-[300px]">
          <AlertCircle className="h-10 w-10 mb-4" />
          <h3 className="text-lg font-semibold">Error Loading Compliance</h3>
          <p className="text-sm mt-2">{error}</p>
        </div>
      </div>
    );
  }

  const hasData = data && (Array.isArray(data) ? data.length > 0 : Object.keys(data).length > 0);

  return (
    <div className="flex flex-col gap-6 p-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Compliance</h1>
        <p className="text-muted-foreground text-sm flex items-center gap-2 mt-2">
          <span>Dashboard</span>
          <span>/</span>
          <span className="text-foreground">Compliance</span>
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
            <p className="text-sm text-muted-foreground mt-2">There are currently no compliance records to display. Check back later or create a new record.</p>
          </div>
        ) : (
          <div className="w-full h-full flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Recent Compliance Data</h3>
            <div className="bg-secondary/30 rounded-lg p-4 overflow-auto max-h-[400px]">
              <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
