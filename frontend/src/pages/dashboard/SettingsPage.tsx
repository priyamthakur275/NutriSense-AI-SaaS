import { useState } from 'react';
import { Bell, Shield, Eye, Palette, Globe, Lock } from 'lucide-react';
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
