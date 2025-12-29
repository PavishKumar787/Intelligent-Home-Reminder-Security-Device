import React, { useState } from 'react';
import { Bell, Plus, Trash2, User, Key, Wallet, CreditCard, Briefcase } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface ReminderItem {
  id: string;
  name: string;
  icon: string;
}

interface UserReminders {
  userId: string;
  userName: string;
  items: ReminderItem[];
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  key: Key,
  wallet: Wallet,
  card: CreditCard,
  briefcase: Briefcase,
  default: Bell,
};

const initialReminders: UserReminders[] = [
  {
    userId: '1',
    userName: 'John Doe',
    items: [
      { id: '1', name: 'Keys', icon: 'key' },
      { id: '2', name: 'Wallet', icon: 'wallet' },
    ],
  },
  {
    userId: '2',
    userName: 'Jane Smith',
    items: [
      { id: '3', name: 'ID Card', icon: 'card' },
      { id: '4', name: 'Laptop Bag', icon: 'briefcase' },
    ],
  },
];

const RemindersPage: React.FC = () => {
  const [reminders, setReminders] = useState<UserReminders[]>(initialReminders);
  const [newItemName, setNewItemName] = useState('');
  const [selectedUser, setSelectedUser] = useState('1');
  const { toast } = useToast();

  const handleAddReminder = () => {
    if (!newItemName.trim()) return;

    setReminders(prev =>
      prev.map(user => {
        if (user.userId === selectedUser) {
          return {
            ...user,
            items: [
              ...user.items,
              {
                id: Date.now().toString(),
                name: newItemName,
                icon: 'default',
              },
            ],
          };
        }
        return user;
      })
    );

    toast({
      title: 'Reminder Added',
      description: `"${newItemName}" has been added to the reminder list.`,
    });
    setNewItemName('');
  };

  const handleRemoveReminder = (userId: string, itemId: string) => {
    setReminders(prev =>
      prev.map(user => {
        if (user.userId === userId) {
          return {
            ...user,
            items: user.items.filter(item => item.id !== itemId),
          };
        }
        return user;
      })
    );

    toast({
      title: 'Reminder Removed',
      description: 'The item has been removed from the reminder list.',
    });
  };

  const getIcon = (iconName: string) => {
    return iconMap[iconName] || iconMap.default;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-success/10 mb-4">
          <Bell className="h-7 w-7 text-success" />
        </div>
        <h1 className="text-2xl font-bold mb-2">Reminder Items</h1>
        <p className="text-muted-foreground">
          Manage items that users should be reminded to take
        </p>
      </div>

      {/* Add Reminder Form */}
      <div className="glass-card rounded-xl p-6 border border-border">
        <h3 className="font-semibold mb-4">Add New Reminder</h3>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 space-y-2">
            <Label htmlFor="user">Select User</Label>
            <select
              id="user"
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              className="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {reminders.map(user => (
                <option key={user.userId} value={user.userId}>
                  {user.userName}
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
              placeholder="e.g., Keys, Wallet, Phone"
              onKeyDown={(e) => e.key === 'Enter' && handleAddReminder()}
            />
          </div>
          <div className="flex items-end">
            <Button
              variant="gradient"
              onClick={handleAddReminder}
              disabled={!newItemName.trim()}
            >
              <Plus className="h-4 w-4" />
              Add Item
            </Button>
          </div>
        </div>
      </div>

      {/* User Reminders List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reminders.map(user => (
          <div
            key={user.userId}
            className="glass-card rounded-xl p-6 border border-border"
          >
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-border">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">{user.userName}</h3>
                <p className="text-xs text-muted-foreground">
                  {user.items.length} reminder{user.items.length !== 1 ? 's' : ''}
                </p>
              </div>
            </div>

            {user.items.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No reminders set
              </p>
            ) : (
              <ul className="space-y-2">
                {user.items.map(item => {
                  const Icon = getIcon(item.icon);
                  return (
                    <li
                      key={item.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Icon className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{item.name}</span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-destructive"
                        onClick={() => handleRemoveReminder(user.userId, item.id)}
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
    </div>
  );
};

export default RemindersPage;
