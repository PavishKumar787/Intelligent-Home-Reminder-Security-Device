import React, { useState, useEffect } from 'react';
import { Bell, Plus, Trash2, User, Key, Wallet, CreditCard, Briefcase, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import api from '@/lib/api';

interface UserWithReminders {
  name: string;
  reminders: string[];
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  key: Key,
  keys: Key,
  wallet: Wallet,
  card: CreditCard,
  id: CreditCard,
  briefcase: Briefcase,
  laptop: Briefcase,
  bag: Briefcase,
  default: Bell,
};

const getIconForItem = (itemName: string) => {
  const lowerName = itemName.toLowerCase();
  for (const [key, icon] of Object.entries(iconMap)) {
    if (lowerName.includes(key)) {
      return icon;
    }
  }
  return iconMap.default;
};

const RemindersPage: React.FC = () => {
  const [users, setUsers] = useState<UserWithReminders[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const { toast } = useToast();

  // Fetch users from backend
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users');
      setUsers(response.data);
      if (response.data.length > 0 && !selectedUser) {
        setSelectedUser(response.data[0].name);
      }
    } catch (error) {
      console.error('Failed to fetch users:', error);
      toast({
        title: 'Error',
        description: 'Failed to load users. Make sure the backend is running.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Save reminders to backend
  const saveReminders = async (userName: string, reminders: string[]) => {
    try {
      setSaving(true);
      await api.post('/update-reminders', {
        name: userName,
        reminders: reminders,
      });
      return true;
    } catch (error) {
      console.error('Failed to save reminders:', error);
      toast({
        title: 'Error',
        description: 'Failed to save reminders.',
        variant: 'destructive',
      });
      return false;
    } finally {
      setSaving(false);
    }
  };

  const handleAddReminder = async () => {
    if (!newItemName.trim() || !selectedUser) return;

    const user = users.find(u => u.name === selectedUser);
    if (!user) return;

    const updatedReminders = [...user.reminders, newItemName.trim()];
    
    const success = await saveReminders(selectedUser, updatedReminders);
    if (success) {
      setUsers(prev =>
        prev.map(u => 
          u.name === selectedUser 
            ? { ...u, reminders: updatedReminders }
            : u
        )
      );

      toast({
        title: 'Reminder Added',
        description: `"${newItemName}" has been added for ${selectedUser}.`,
      });
      setNewItemName('');
    }
  };

  const handleRemoveReminder = async (userName: string, itemToRemove: string) => {
    const user = users.find(u => u.name === userName);
    if (!user) return;

    const updatedReminders = user.reminders.filter(item => item !== itemToRemove);
    
    const success = await saveReminders(userName, updatedReminders);
    if (success) {
      setUsers(prev =>
        prev.map(u => 
          u.name === userName 
            ? { ...u, reminders: updatedReminders }
            : u
        )
      );

      toast({
        title: 'Reminder Removed',
        description: `"${itemToRemove}" has been removed.`,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading users...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-success/10 mb-4">
          <Bell className="h-7 w-7 text-success" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Reminder Items</h1>
        <p className="text-muted-foreground">
          Set items that users should be reminded to take when leaving
        </p>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-end">
        <Button variant="outline" onClick={fetchUsers} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Users
        </Button>
      </div>

      {users.length === 0 ? (
        <div className="glass-card rounded-xl p-8 border border-border text-center">
          <User className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-semibold mb-2">No Users Enrolled</h3>
          <p className="text-muted-foreground mb-4">
            Enroll users first to set their reminder items.
          </p>
          <Button variant="gradient" onClick={() => window.location.href = '/enroll'}>
            Go to Enrollment
          </Button>
        </div>
      ) : (
        <>
          {/* Add Reminder Form */}
          <div className="glass-card rounded-xl p-6 border border-border">
            <h3 className="font-semibold mb-4">Add New Reminder Item</h3>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 space-y-2">
                <Label htmlFor="user">Select User</Label>
                <select
                  id="user"
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  {users.map(user => (
                    <option key={user.name} value={user.name}>
                      {user.name.charAt(0).toUpperCase() + user.name.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex-1 space-y-2">
                <Label htmlFor="item">Item Name</Label>
                <Input
                  id="item"
                  type="text"
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                  placeholder="e.g., Keys, Wallet, Phone, Laptop"
                  onKeyDown={(e) => e.key === 'Enter' && handleAddReminder()}
                />
              </div>
              <div className="flex items-end">
                <Button
                  variant="gradient"
                  onClick={handleAddReminder}
                  disabled={!newItemName.trim() || saving}
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                  Add Item
                </Button>
              </div>
            </div>
          </div>

          {/* User Reminders List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {users.map(user => (
              <div
                key={user.name}
                className="glass-card rounded-xl p-6 border border-border"
              >
                <div className="flex items-center gap-3 mb-4 pb-4 border-b border-border">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold capitalize">{user.name}</h3>
                    <p className="text-xs text-muted-foreground">
                      {user.reminders.length} reminder{user.reminders.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>

                {user.reminders.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No reminders set. Add items this person should remember to take.
                  </p>
                ) : (
                  <ul className="space-y-2">
                    {user.reminders.map((item, index) => {
                      const Icon = getIconForItem(item);
                      return (
                        <li
                          key={`${user.name}-${index}`}
                          className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <Icon className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium">{item}</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-muted-foreground hover:text-destructive"
                            onClick={() => handleRemoveReminder(user.name, item)}
                            disabled={saving}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default RemindersPage;
