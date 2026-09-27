import os

base_dir = r"c:\Users\priya\Downloads\nutrisense-ai (2)\frontend\src"

profile_page_tsx = """import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Camera, User, Mail, Shield, Key, MapPin, Phone, History, LogOut, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { toast } from 'sonner';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const handleSave = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      toast.success('Profile updated successfully');
    }, 1000);
  };

  return (
    <div className="flex flex-col gap-6 p-6 md:p-8 max-w-5xl mx-auto w-full animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">User Profile</h1>
        <p className="text-muted-foreground text-sm mt-1">Manage your personal information and security settings.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 flex flex-col gap-6">
          <Card className="text-center shadow-sm">
            <CardContent className="pt-6">
              <div className="relative w-32 h-32 mx-auto mb-4 group cursor-pointer">
                <div className="w-full h-full rounded-full bg-primary/10 border-4 border-background shadow-xl flex items-center justify-center overflow-hidden">
                  <User className="w-12 h-12 text-primary/50" />
                </div>
                <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="w-8 h-8 text-white" />
                </div>
                <div className="absolute bottom-0 right-0 p-2 bg-primary text-primary-foreground rounded-full shadow-lg cursor-pointer">
                  <Camera size={16} />
                </div>
              </div>
              <h3 className="text-xl font-bold">{user?.name || 'Jane Doe'}</h3>
              <p className="text-muted-foreground text-sm capitalize">{user?.role || 'Administrator'}</p>
              <div className="mt-6 space-y-2 text-sm text-left">
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Mail size={16} /> <span>{user?.email || 'user@example.com'}</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Phone size={16} /> <span>+1 (555) 123-4567</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <MapPin size={16} /> <span>New York, USA</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-sm">
             <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2"><Shield size={18} /> Account Status</CardTitle>
             </CardHeader>
             <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                   <span className="text-sm">Email Verification</span>
                   <span className="flex items-center gap-1 text-emerald-500 text-sm font-medium"><CheckCircle2 size={14} /> Verified</span>
                </div>
                <div className="flex justify-between items-center">
                   <span className="text-sm">Two-Factor Auth</span>
                   <span className="flex items-center gap-1 text-amber-500 text-sm font-medium"><AlertCircle size={14} /> Disabled</span>
                </div>
             </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 flex flex-col gap-6">
          <Card className="shadow-sm">
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">First Name</label>
                    <input type="text" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" defaultValue={user?.name?.split(' ')[0] || 'Jane'} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Last Name</label>
                    <input type="text" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" defaultValue={user?.name?.split(' ')[1] || 'Doe'} />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email Address</label>
                  <input type="email" disabled className="w-full bg-muted/50 border border-border rounded-md px-3 py-2 text-sm cursor-not-allowed text-muted-foreground" defaultValue={user?.email || 'user@example.com'} />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Bio</label>
                  <textarea rows={3} className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" placeholder="A short bio about yourself..." defaultValue="Senior nutritionist managing dietary requirements." />
                </div>
                <Button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Save Changes'}</Button>
              </form>
            </CardContent>
          </Card>

          <Card className="shadow-sm border-red-500/20">
            <CardHeader>
              <CardTitle className="text-red-500 flex items-center gap-2"><Key size={18} /> Security & Passwords</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Password</label>
                  <input type="password" placeholder="••••••••" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">New Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Confirm Password</label>
                    <input type="password" placeholder="••••••••" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" />
                  </div>
                </div>
                <Button type="button" variant="outline" className="text-red-500 hover:text-red-600 hover:bg-red-500/10">Update Password</Button>
              </form>
            </CardContent>
          </Card>
          
          <Card className="shadow-sm">
             <CardHeader>
                <CardTitle className="flex items-center gap-2"><History size={18} /> Recent Activity</CardTitle>
             </CardHeader>
             <CardContent>
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2.5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                   {[1,2,3].map(i => (
                      <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                         <div className="flex items-center justify-center w-6 h-6 rounded-full border border-white bg-slate-300 text-slate-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow" />
                         <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-slate-200 bg-white dark:bg-slate-800 dark:border-slate-700 shadow">
                            <div className="flex items-center justify-between space-x-2 mb-1">
                               <div className="font-bold text-slate-900 dark:text-slate-100">Logged in</div>
                               <time className="font-caveat font-medium text-indigo-500">Just now</time>
                            </div>
                            <div className="text-slate-500 dark:text-slate-400 text-sm">Successfully authenticated via IP 192.168.1.{i}</div>
                         </div>
                      </div>
                   ))}
                </div>
             </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
"""

settings_page_tsx = """import { useState } from 'react';
import { Settings, Bell, Shield, Eye, Palette, Globe, Smartphone, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useThemeStore } from '@/store/themeStore';
import { toast } from 'sonner';

export default function SettingsPage() {
  const { theme, setTheme } = useThemeStore();
  const [activeTab, setActiveTab] = useState('appearance');

  const handleSave = () => {
    toast.success('Settings saved successfully');
  };

  return (
    <div className="flex flex-col gap-6 p-6 md:p-8 max-w-6xl mx-auto w-full animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">System Settings</h1>
        <p className="text-muted-foreground text-sm mt-1">Configure your workspace, notifications, and privacy preferences.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6 mt-4">
        {/* Sidebar */}
        <div className="w-full md:w-64 flex flex-col gap-1">
          {[
            { id: 'appearance', label: 'Appearance', icon: Palette },
            { id: 'notifications', label: 'Notifications', icon: Bell },
            { id: 'privacy', label: 'Privacy & Security', icon: Shield },
            { id: 'accessibility', label: 'Accessibility', icon: Eye },
            { id: 'language', label: 'Language & Region', icon: Globe },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'hover:bg-muted text-muted-foreground'
              }`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'appearance' && (
            <Card className="shadow-sm animate-in fade-in slide-in-from-right-4">
              <CardHeader>
                <CardTitle>Appearance Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="text-sm font-medium mb-3">Theme Preference</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {['light', 'dark', 'system'].map(t => (
                      <div 
                        key={t}
                        onClick={() => setTheme(t as any)}
                        className={`border-2 rounded-xl p-4 cursor-pointer flex flex-col items-center gap-2 transition-all ${
                          theme === t ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <div className={`w-full h-16 rounded-md mb-2 ${t === 'dark' ? 'bg-slate-900' : t === 'light' ? 'bg-slate-100' : 'bg-gradient-to-r from-slate-100 to-slate-900'}`} />
                        <span className="capitalize text-sm font-medium">{t}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="border-t pt-6">
                   <Button onClick={handleSave}>Save Preferences</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card className="shadow-sm animate-in fade-in slide-in-from-right-4">
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { title: 'Email Notifications', desc: 'Receive daily summary emails' },
                  { title: 'Push Notifications', desc: 'Real-time alerts for critical issues' },
                  { title: 'SMS Alerts', desc: 'Text messages for compliance failures' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{item.title}</p>
                      <p className="text-muted-foreground text-sm">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={i < 2} />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                    </label>
                  </div>
                ))}
                <div className="border-t pt-6">
                   <Button onClick={handleSave}>Save Preferences</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {['privacy', 'accessibility', 'language'].includes(activeTab) && (
            <Card className="shadow-sm animate-in fade-in slide-in-from-right-4 h-[400px] flex items-center justify-center text-center">
              <CardContent>
                 <Lock className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
                 <h3 className="text-lg font-semibold">Additional Settings</h3>
                 <p className="text-muted-foreground text-sm max-w-sm mt-2">These enterprise configurations are managed by your system administrator.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
"""

notifications_page_tsx = """import { useState } from 'react';
import { Bell, Check, Trash2, Filter, Search, ShieldAlert, CheckCircle, Info } from 'lucide-react';
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
"""

with open(os.path.join(base_dir, "pages/dashboard/ProfilePage.tsx"), "w", encoding="utf-8") as f:
    f.write(profile_page_tsx)

with open(os.path.join(base_dir, "pages/dashboard/SettingsPage.tsx"), "w", encoding="utf-8") as f:
    f.write(settings_page_tsx)

with open(os.path.join(base_dir, "pages/dashboard/NotificationsPage.tsx"), "w", encoding="utf-8") as f:
    f.write(notifications_page_tsx)

print("UX improvements applied.")
