import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { Search, Filter, Download, Edit, Eye, Plus, Camera, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { toast } from 'sonner';

export default function MealsPage() {
  const [loading, setLoading] = useState(true);
  const [meals, setMeals] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [sortBy, setSortBy] = useState('served_at');
  const [sortDesc, setSortDesc] = useState(true);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(handler);
  }, [search]);

  const fetchMeals = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        size: size.toString(),
        sort_by: sortBy,
        sort_desc: sortDesc.toString(),
      });
      if (debouncedSearch) params.append('search', debouncedSearch);

      const response = await api.get(`/meals?${params.toString()}`);
      setMeals(response.data.items || []);
      setTotal(response.data.total_items || 0);
    } catch (err: any) {
      toast.error('Failed to load meals');
    } finally {
      setLoading(false);
    }
  }, [page, size, sortBy, sortDesc, debouncedSearch]);

  useEffect(() => {
    fetchMeals();
  }, [fetchMeals]);

  const toggleSort = (col: string) => {
    if (sortBy === col) setSortDesc(!sortDesc);
    else { setSortBy(col); setSortDesc(false); }
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) setSelectedIds(new Set(meals.map(m => m.id)));
    else setSelectedIds(new Set());
  };

  const handleSelect = (id: string, checked: boolean) => {
    const newSet = new Set(selectedIds);
    if (checked) newSet.add(id);
    else newSet.delete(id);
    setSelectedIds(newSet);
  };

  const getStatusBadge = (status: string) => {
    switch(status.toLowerCase()) {
      case 'served': return <Badge className="bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20">Served</Badge>;
      case 'planned': return <Badge className="bg-blue-500/10 text-blue-600 hover:bg-blue-500/20">Planned</Badge>;
      case 'cancelled': return <Badge className="bg-red-500/10 text-red-600 hover:bg-red-500/20">Cancelled</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6 md:p-8 animate-in fade-in duration-500 max-w-7xl mx-auto w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meals Registry</h1>
          <p className="text-muted-foreground text-sm mt-1">Track and manage institutional meal plans and servings.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2 bg-background">
            <Download size={16} /> Export
          </Button>
          <Button className="gap-2">
            <Plus size={16} /> Log Meal
          </Button>
        </div>
      </div>

      <Card className="flex flex-col shadow-sm border-border/50">
        <div className="p-4 border-b flex flex-col sm:flex-row justify-between gap-4 bg-muted/10 rounded-t-xl">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search meals..." 
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
                  <input type="checkbox" checked={meals.length > 0 && selectedIds.size === meals.length} onChange={handleSelectAll} className="rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                </TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('name')}>
                  Meal Name {sortBy === 'name' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('meal_type')}>
                  Type {sortBy === 'meal_type' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('status')}>
                  Status {sortBy === 'status' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="cursor-pointer hover:text-foreground" onClick={() => toggleSort('served_at')}>
                  Date Served {sortBy === 'served_at' && (sortDesc ? '↓' : '↑')}
                </TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                 Array.from({ length: 5 }).map((_, i) => (
                   <TableRow key={i}>
                     <TableCell><Skeleton className="h-4 w-4 rounded" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                     <TableCell><Skeleton className="h-5 w-20 rounded-full" /></TableCell>
                     <TableCell><Skeleton className="h-5 w-20 rounded-full" /></TableCell>
                     <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                     <TableCell><Skeleton className="h-8 w-8 rounded ml-auto" /></TableCell>
                   </TableRow>
                 ))
              ) : meals.length === 0 ? (
                 <TableRow>
                   <TableCell colSpan={6} className="h-48 text-center text-muted-foreground">
                     <div className="flex flex-col items-center justify-center gap-2">
                       <Search className="h-8 w-8 opacity-20" />
                       <p>No meals found matching your criteria.</p>
                     </div>
                   </TableCell>
                 </TableRow>
              ) : (
                meals.map((meal) => (
                  <TableRow key={meal.id} className="group">
                    <TableCell className="text-center">
                      <input type="checkbox" checked={selectedIds.has(meal.id)} onChange={(e) => handleSelect(meal.id, e.target.checked)} className="rounded border-gray-300 text-primary focus:ring-primary cursor-pointer" />
                    </TableCell>
                    <TableCell className="font-medium flex items-center gap-2">
                      <div className="h-8 w-8 bg-muted rounded flex items-center justify-center"><Camera size={14} className="text-muted-foreground" /></div>
                      {meal.name}
                    </TableCell>
                    <TableCell><Badge variant="outline" className="capitalize">{meal.meal_type}</Badge></TableCell>
                    <TableCell>{getStatusBadge(meal.status)}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {meal.served_at ? new Date(meal.served_at).toLocaleString() : 'N/A'}
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
          <div>Showing {meals.length > 0 ? (page - 1) * size + 1 : 0} to {Math.min(page * size, total)} of {total} results</div>
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
