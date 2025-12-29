import React from 'react';
import { AlertTriangle, Bell, Shield, Clock, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Alert } from '@/lib/api';

interface AlertCardProps {
  alert: Alert;
  className?: string;
}

const alertConfig = {
  motion: {
    icon: Activity,
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary/30',
    iconColor: 'text-primary',
    badgeColor: 'bg-primary/20 text-primary',
  },
  emergency: {
    icon: AlertTriangle,
    bgColor: 'bg-destructive/10',
    borderColor: 'border-destructive/30',
    iconColor: 'text-destructive',
    badgeColor: 'bg-destructive/20 text-destructive',
  },
  security: {
    icon: Shield,
    bgColor: 'bg-warning/10',
    borderColor: 'border-warning/30',
    iconColor: 'text-warning',
    badgeColor: 'bg-warning/20 text-warning',
  },
  reminder: {
    icon: Bell,
    bgColor: 'bg-success/10',
    borderColor: 'border-success/30',
    iconColor: 'text-success',
    badgeColor: 'bg-success/20 text-success',
  },
} as const;

// 🔒 SAFE FALLBACK (prevents crashes forever)
const fallbackConfig = {
  icon: Bell,
  bgColor: 'bg-muted/10',
  borderColor: 'border-muted/30',
  iconColor: 'text-muted-foreground',
  badgeColor: 'bg-muted/20 text-muted-foreground',
};

const AlertCard: React.FC<AlertCardProps> = ({ alert, className }) => {
  // ✅ Normalize backend type → frontend key
  const typeKey = alert.type?.toLowerCase() as keyof typeof alertConfig;

  const config = alertConfig[typeKey] ?? fallbackConfig;
  const Icon = config.icon;

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className={cn(
        'glass-card rounded-xl p-4 border transition-all duration-300 hover:shadow-glow animate-fade-in',
        config.bgColor,
        config.borderColor,
        !alert.read && 'ring-2 ring-primary/20',
        className
      )}
    >
      <div className="flex items-start gap-4">
        <div className={cn('p-2.5 rounded-lg', config.bgColor)}>
          <Icon className={cn('h-5 w-5', config.iconColor)} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={cn(
                'px-2 py-0.5 rounded-full text-xs font-medium capitalize',
                config.badgeColor
              )}
            >
              {typeKey ?? 'alert'}
            </span>

            {!alert.read && (
              <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            )}
          </div>

          <p className="text-sm font-medium text-foreground mb-1">
            {alert.message}
          </p>

          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{formatTime(alert.timestamp)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertCard;
