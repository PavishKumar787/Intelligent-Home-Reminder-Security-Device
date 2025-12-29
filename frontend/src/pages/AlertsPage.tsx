import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AlertCard from '@/components/shared/AlertCard';
import { alertsApi, type Alert } from '@/lib/api';
import { cn } from '@/lib/utils';

type AlertFilter = 'all' | Alert['type'];

const AlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState<AlertFilter>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchAlerts = async () => {
    setIsRefreshing(true);
    const data = await alertsApi.getAlerts();
    setAlerts(data);
    setIsRefreshing(false);
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredAlerts =
    filter === 'all'
      ? alerts
      : alerts.filter(a => a.type === filter);

  const filterOptions: { value: AlertFilter; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'motion', label: 'Motion' },
    { value: 'emergency', label: 'Emergency' },
    { value: 'security', label: 'Security' },
    { value: 'reminder', label: 'Reminder' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-warning/10 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-warning" />
            </div>
            <h1 className="text-2xl font-bold">Alerts</h1>
          </div>
          <p className="text-muted-foreground">
            View and manage all system alerts
          </p>
        </div>

        <Button variant="outline" onClick={fetchAlerts} disabled={isRefreshing}>
          <RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin')} />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {filterOptions.map(option => (
          <Button
            key={option.value}
            variant={filter === option.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12 glass-card rounded-xl border border-border">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-semibold mb-2">No Alerts</h3>
            <p className="text-sm text-muted-foreground">
              {filter === 'all'
                ? 'No alerts to display at this time.'
                : `No ${filter} alerts found.`}
            </p>
          </div>
        ) : (
          filteredAlerts.map((alert, index) => (
            <AlertCard
              key={alert.id || (alert as any)._id || index}
              alert={alert}
            />
          ))
        )}
      </div>

      <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
        <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
        Auto-refreshing every 10 seconds
      </div>
    </div>
  );
};

export default AlertsPage;
