import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { Search, Filter, Download, Edit, Eye, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { toast } from 'sonner';

export default function NutritionPage() {
  const [loading, setLoading] = useState(true);
  const [records, setRecords] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [search, setSearch] = useState(''); // Client-side fallback if no backend support
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortDesc, setSortDesc] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(handler);
  }, [search]);

  const fetchRecords = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
        sort_by: sortBy,
        sort_desc: sortDesc.toString(),
      });
      // The backend /nutrition-records doesn't support 'search' natively, but we pass it anyway.
      // In a real scenario we'd do client-side filtering if backend drops it.
      
      const response = await api.get(`/nutrition-records?${params.toString()}`);
      
      let data = response.data.items || [];
      if (debouncedSearch) {
         // Client side filtering as fallback
         const lowerSearch = debouncedSearch.toLowerCase();
         data = data.filter((r: any) => 
            r.id.toLowerCase().includes(lowerSearch) || 
            (r.meal_id && r.meal_id.toLowerCase().includes(lowerSearch))
         );
      }
      setRecords(data);
      setTotal(response.data.total_items || data.length);
    } catch (err: any) {
      toast.error('Failed to load nutrition records');
    } finally {
      setLoading(false);
    }
  }, [page, size, sortBy, sortDesc, debouncedSearch]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  const toggleSort = (col: string) => {
    if (sortBy === col) setSortDesc(!sortDesc);
    else { setSortBy(col); setSortDesc(false); }
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) setSelectedIds(new Set(records.map(r => r.id)));
    else setSelectedIds(new Set());
  };

  const handleSelect = (id: string, checked: boolean) => {
    const newSet = new Set(selectedIds);
    if (checked) newSet.add(id);
    else newSet.delete(id);
    setSelectedIds(newSet);
  };

  const getComplianceBadge = (score: number | null) => {
    if (score === null || score === undefined) return <Badge variant="outline">N/A</Badge>;
    if (score >= 80) return <Badge className="bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20">{score.toFixed(1)}%</Badge>;
    if (score >= 50) return <Badge className="bg-amber-500/10 text-amber-600 hover:bg-amber-500/20">{score.toFixed(1)}%</Badge>;
    return <Badge className="bg-red-500/10 text-red-600 hover:bg-red-500/20">{score.toFixed(1)}%</Badge>;
  };

  return (
    <div className="flex flex-col gap-6 p-6 md:p-8 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Nutrition Records</h1>
          <p className="text-muted-foreground text-sm mt-1">Detailed nutritional breakdowns and compliance scores for all logged meals.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2 bg-background">
            <Download size={16} /> Export
          </Button>
          <Button className="gap-2">
            <Plus size={16} /> Manual Entry
          </Button>
        </div>
      </div>

      <Card className="flex flex-col shadow-sm border-border/50">
        <div className="p-4 border-b flex flex-col sm:flex-row justify-between gap-4 bg-muted/10 rounded-t-xl">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search records by ID..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
          <div className="flex items-center gap-2">
            {selectedIds.size > 0 && (
               <div className="flex items-center gap-2 mr-4 px-3 py-1 bg-primary/10 text-primary rounded-md text-sm font-medium animate-in slide-in-from-right-4">
                 <span>{selectedIds.size} selected</span>
                 <Button variant="ghost" size="sm" className="h-6 px-2 text-red-500" onClick={() => setSelectedIds(new Set())}>Clear</Button>
               </div>
            )}
            <Button variant="outline" size="sm" className="gap-2 h-9"><Filter size={14} /> Filter</Button>
          </div>
        </div>

        <div className="relative w-full overflow-auto min-h-[400px]">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/30 hover:bg-muted/30">
                <TableHead className="w-12 text-center">
                  <input type="checkbox" checked={records.length > 0 && selectedIds.size === records.length} onChange={handleSelectAll} className="rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                </TableHead>
                <TableHead>Record ID</TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('calories_kcal')}>
                  Calories {sortBy === 'calories_kcal' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead>Macros (P/C/F)</TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('compliance_score')}>
                  Compliance {sortBy === 'compliance_score' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('created_at')}>
                  Created At {sortBy === 'created_at' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                 Array.from({ length: 5 }).map((_, i) => (
                   <TableRow key={i}>
                     <TableCell><Skeleton className="h-4 w-4 rounded" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                     <TableCell><Skeleton className="h-5 w-16 rounded-full" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                     <TableCell><Skeleton className="h-8 w-8 rounded ml-auto" /></TableCell>
                   </TableRow>
                 ))
              ) : records.length === 0 ? (
                 <TableRow>
                   <TableCell colSpan={7} className="h-48 text-center text-muted-foreground">
                     <div className="flex flex-col items-center justify-center gap-2">
                       <Search className="h-8 w-8 opacity-20" />
                       <p>No nutrition records found matching your criteria.</p>
                     </div>
                   </TableCell>
                 </TableRow>
              ) : (
                records.map((record) => (
                  <TableRow key={record.id} className="group">
                    <TableCell className="text-center">
                      <input type="checkbox" checked={selectedIds.has(record.id)} onChange={(e) => handleSelect(record.id, e.target.checked)} className="rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                    </TableCell>
                    <TableCell className="font-medium text-muted-foreground font-mono text-sm">
                      {record.id.substring(0,8)}...
                    </TableCell>
                    <TableCell>{record.calories_kcal ? `${Math.round(record.calories_kcal)} kcal` : 'N/A'}</TableCell>
                    <TableCell className="text-sm">
                      <span className="text-emerald-500 font-medium">{record.protein_g ? Math.round(record.protein_g) : 0}g</span> / {' '}
                      <span className="text-blue-500 font-medium">{record.carbs_g ? Math.round(record.carbs_g) : 0}g</span> / {' '}
                      <span className="text-amber-500 font-medium">{record.fat_g ? Math.round(record.fat_g) : 0}g</span>
                    </TableCell>
                    <TableCell>{getComplianceBadge(record.compliance_score)}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {new Date(record.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary"><Eye size={16} /></Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-primary"><Edit size={16} /></Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        
        <div className="p-4 border-t flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-muted-foreground bg-muted/10 rounded-b-xl">
          <div>Showing {records.length > 0 ? (page - 1) * size + 1 : 0} to {Math.min(page * size, total)} of {total} results</div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span>Rows per page</span>
              <select className="bg-background border rounded px-2 py-1" value={size} onChange={(e) => { setSize(Number(e.target.value)); setPage(1); }}>
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
              </select>
            </div>
            <div className="flex items-center gap-1">
              <Button variant="outline" size="icon" className="h-8 w-8" disabled={page === 1} onClick={() => setPage(p => p - 1)}><ChevronLeft size={16} /></Button>
              <Button variant="outline" size="icon" className="h-8 w-8" disabled={page * size >= total} onClick={() => setPage(p => p + 1)}><ChevronRight size={16} /></Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
