import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Camera, User, Mail, Shield, Key, MapPin, Phone, History, CheckCircle2, AlertCircle } from 'lucide-react';
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
              <h3 className="text-xl font-bold">Jane Doe</h3>
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
                    <input type="text" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" defaultValue="Jane" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Last Name</label>
                    <input type="text" className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50" defaultValue="Doe" />
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
