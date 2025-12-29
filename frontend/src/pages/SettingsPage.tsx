import React from 'react';
import { Settings, User, Moon, Sun, LogOut, Shield, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';

const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-secondary mb-4">
          <Settings className="h-7 w-7 text-foreground" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and preferences
        </p>
      </div>

      {/* Profile Section */}
      <div className="glass-card rounded-xl p-6 border border-border">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <User className="h-4 w-4" />
          Profile Information
        </h3>
        
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <span className="text-2xl font-bold text-primary-foreground">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div>
            <p className="text-lg font-semibold">{user?.name || 'User'}</p>
            <p className="text-sm text-muted-foreground">{user?.email || 'user@example.com'}</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">User ID</span>
            <span className="text-sm font-medium">{user?.id || '1'}</span>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">Role</span>
            <span className="text-sm font-medium">Administrator</span>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">Account Status</span>
            <span className="text-xs px-2 py-1 rounded-full bg-success/20 text-success font-medium">
              Active
            </span>
          </div>
        </div>
      </div>

      {/* Appearance Section */}
      <div className="glass-card rounded-xl p-6 border border-border">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          Appearance
        </h3>
        
        <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-2 rounded-lg',
              theme === 'dark' ? 'bg-primary/20' : 'bg-warning/20'
            )}>
              {theme === 'dark' ? (
                <Moon className="h-4 w-4 text-primary" />
              ) : (
                <Sun className="h-4 w-4 text-warning" />
              )}
            </div>
            <div>
              <Label htmlFor="dark-mode" className="font-medium">Dark Mode</Label>
              <p className="text-xs text-muted-foreground">
                Toggle between light and dark theme
              </p>
            </div>
          </div>
          <Switch
            id="dark-mode"
            checked={theme === 'dark'}
            onCheckedChange={toggleTheme}
          />
        </div>
      </div>

      {/* System Section */}
      <div className="glass-card rounded-xl p-6 border border-border">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Shield className="h-4 w-4" />
          System Information
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">System Version</span>
            <span className="text-sm font-medium">v1.0.0</span>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">Camera Status</span>
            <span className="flex items-center gap-2 text-sm font-medium">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              Online
            </span>
          </div>
          <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/50">
            <span className="text-sm text-muted-foreground">Face Recognition</span>
            <span className="flex items-center gap-2 text-sm font-medium">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              Active
            </span>
          </div>
        </div>
      </div>

      {/* Notifications Section */}
      <div className="glass-card rounded-xl p-6 border border-border">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Bell className="h-4 w-4" />
          Notifications
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
            <div>
              <p className="text-sm font-medium">Motion Alerts</p>
              <p className="text-xs text-muted-foreground">Notify on motion detection</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
            <div>
              <p className="text-sm font-medium">Unknown Person Alerts</p>
              <p className="text-xs text-muted-foreground">Notify when stranger detected</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50">
            <div>
              <p className="text-sm font-medium">Reminder Alerts</p>
              <p className="text-xs text-muted-foreground">Notify for item reminders</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </div>

      {/* Logout Button */}
      <Button
        variant="destructive"
        className="w-full"
        onClick={handleLogout}
      >
        <LogOut className="h-4 w-4" />
        Sign Out
      </Button>
    </div>
  );
};

export default SettingsPage;
