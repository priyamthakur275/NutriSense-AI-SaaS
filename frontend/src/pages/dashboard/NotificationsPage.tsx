import { useState } from 'react';
import { Bell, Check, Trash2, Search, ShieldAlert, CheckCircle, Info } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { toast } from 'sonner';

export default function NotificationsPage() {
  const [activeFilter, setActiveFilter] = useState('all');
  const [search, setSearch] = useState('');
  
  const [notifications, setNotifications] = useState([
    { id: 1, type: 'alert', title: 'High Risk Detected', desc: 'Student #4521 shows severe calorie deficit over 3 days.', time: '2 mins ago', unread: true },
    { id: 2, type: 'success', title: 'Report Generated', desc: 'Weekly compliance report has been published successfully.', time: '1 hour ago', unread: true },
    { id: 3, type: 'info', title: 'System Update', desc: 'New AI models have been deployed to the recommendation engine.', time: 'Yesterday', unread: false },
    { id: 4, type: 'alert', title: 'Missing Data', desc: 'Breakfast logs missing for Grade 10 department.', time: 'Yesterday', unread: false },
  ]);

  const handleMarkAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, unread: false })));
    toast.success('All notifications marked as read');
  };

  const handleDelete = (id: number) => {
    setNotifications(notifications.filter(n => n.id !== id));
    toast.success('Notification dismissed');
  };

  const filtered = notifications.filter(n => {
    if (activeFilter === 'unread' && !n.unread) return false;
    if (search && !n.title.toLowerCase().includes(search.toLowerCase()) && !n.desc.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const getIcon = (type: string) => {
    if (type === 'alert') return <ShieldAlert className="text-red-500" size={20} />;
    if (type === 'success') return <CheckCircle className="text-emerald-500" size={20} />;
    return <Info className="text-blue-500" size={20} />;
  };

  return (
    <div className="flex flex-col gap-6 p-6 md:p-8 max-w-5xl mx-auto w-full animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notification Center</h1>
          <p className="text-muted-foreground text-sm mt-1">Review alerts, reports, and system announcements.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2" onClick={handleMarkAllRead}>
            <Check size={16} /> Mark all read
          </Button>
        </div>
      </div>

      <Card className="shadow-sm border-border/50">
        <div className="p-4 border-b flex flex-col sm:flex-row justify-between gap-4 bg-muted/10 rounded-t-xl">
          <div className="flex gap-2">
             <Button variant={activeFilter === 'all' ? 'default' : 'outline'} size="sm" onClick={() => setActiveFilter('all')}>All</Button>
             <Button variant={activeFilter === 'unread' ? 'default' : 'outline'} size="sm" onClick={() => setActiveFilter('unread')}>
               Unread {notifications.filter(n => n.unread).length > 0 && <Badge className="ml-2 bg-white/20 px-1.5">{notifications.filter(n => n.unread).length}</Badge>}
             </Button>
          </div>
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search notifications..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-background border border-border rounded-md pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
        </div>
        
        <CardContent className="p-0">
          {filtered.length === 0 ? (
             <div className="p-16 flex flex-col items-center justify-center text-muted-foreground text-center">
                <Bell className="h-12 w-12 mb-4 opacity-20" />
                <h3 className="text-lg font-semibold">You're all caught up!</h3>
                <p className="max-w-sm mt-2 text-sm">There are no notifications matching your criteria.</p>
             </div>
          ) : (
            <div className="divide-y divide-border">
              {filtered.map(notification => (
                <div key={notification.id} className={`p-4 flex gap-4 transition-colors hover:bg-muted/50 group ${notification.unread ? 'bg-primary/5' : ''}`}>
                  <div className="pt-1">{getIcon(notification.type)}</div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                       <h4 className={`text-sm font-semibold ${notification.unread ? 'text-foreground' : 'text-foreground/80'}`}>{notification.title}</h4>
                       <span className="text-xs text-muted-foreground whitespace-nowrap ml-4">{notification.time}</span>
                    </div>
                    <p className={`text-sm ${notification.unread ? 'text-foreground/90 font-medium' : 'text-muted-foreground'}`}>{notification.desc}</p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center px-2">
                     <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-red-500" onClick={() => handleDelete(notification.id)}>
                        <Trash2 size={16} />
                     </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
