import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Shield, Bell, Users, Eye, Package } from 'lucide-react';
import StatCard from '@/components/shared/StatCard';
import AlertCard from '@/components/shared/AlertCard';
import CameraBox from '@/components/shared/CameraBox';
import { alertsApi, type Alert } from '@/lib/api';
import { BASE_URL } from '@/config';

const DashboardPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [detectedPerson, setDetectedPerson] = useState<{
    name: string;
    isKnown: boolean;
    reminders: string[];
  } | null>(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      const data = await alertsApi.getAlerts();
      setAlerts(data);
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  // Fetch real detection from API
  useEffect(() => {
    const fetchDetection = async () => {
      try {
        const res = await fetch(`${BASE_URL}/current-detection`);
        const data = await res.json();
        
        // Only show if there's an actual detection
        if (data.name) {
          setDetectedPerson({
            name: data.name,
            isKnown: data.isKnown,
            reminders: data.reminders || [],
          });
        } else {
          setDetectedPerson(null);
        }
      } catch (error) {
        console.error('Failed to fetch detection:', error);
        setDetectedPerson(null);
      }
    };

    fetchDetection();
    const interval = setInterval(fetchDetection, 2000);
    return () => clearInterval(interval);
  }, []);

  const alertCounts = {
    motion: alerts.filter(a => a.type === 'motion').length,
    emergency: alerts.filter(a => a.type === 'emergency').length,
    security: alerts.filter(a => a.type === 'security').length,
    reminder: alerts.filter(a => a.type === 'reminder').length,
  };

  const recentAlerts = alerts.slice(0, 4);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Motion Alerts"
          value={alertCounts.motion}
          icon={Activity}
          variant="primary"
          trend="up"
          trendValue="12% from yesterday"
        />
        <StatCard
          title="Emergency Alerts"
          value={alertCounts.emergency}
          icon={AlertTriangle}
          variant="destructive"
        />
        <StatCard
          title="Security Alerts"
          value={alertCounts.security}
          icon={Shield}
          variant="warning"
        />
        <StatCard
          title="Reminders"
          value={alertCounts.reminder}
          icon={Bell}
          variant="success"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera Feed */}
        <div className="lg:col-span-2">
          <CameraBox isLive={true} detectedPerson={detectedPerson} />
        </div>

        {/* Detection Status */}
        <div className="glass-card rounded-xl p-5 border border-border">
          <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
            <Eye className="h-4 w-4 text-primary" />
            Detection Status
          </h3>

          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-secondary/50 border border-border">
              <p className="text-xs text-muted-foreground mb-2">
                Current Detection
              </p>
              {detectedPerson ? (
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      detectedPerson.isKnown
                        ? 'bg-success/20'
                        : detectedPerson.name === 'Motion Detected'
                        ? 'bg-blue-500/20'
                        : 'bg-destructive/20'
                    }`}
                  >
                    <Users
                      className={`h-5 w-5 ${
                        detectedPerson.isKnown
                          ? 'text-success'
                          : detectedPerson.name === 'Motion Detected'
                          ? 'text-blue-500'
                          : 'text-destructive'
                      }`}
                    />
                  </div>
                  <div>
                    <p className="font-medium capitalize">{detectedPerson.name}</p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        detectedPerson.isKnown
                          ? 'bg-success/20 text-success'
                          : detectedPerson.name === 'Motion Detected'
                          ? 'bg-blue-500/20 text-blue-500'
                          : 'bg-destructive/20 text-destructive'
                      }`}
                    >
                      {detectedPerson.isKnown
                        ? 'Known User'
                        : detectedPerson.name === 'Motion Detected'
                        ? 'Motion Activity'
                        : 'Unknown Person'}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No person detected
                </p>
              )}
            </div>

            {/* Reminders Section - Only show for known users with reminders */}
            {detectedPerson?.isKnown && detectedPerson.reminders.length > 0 && (
              <div className="p-4 rounded-lg bg-warning/10 border border-warning/30">
                <div className="flex items-center gap-2 mb-3">
                  <Bell className="h-4 w-4 text-warning" />
                  <p className="text-sm font-semibold text-warning">
                    Don't forget to take:
                  </p>
                </div>
                <ul className="space-y-2">
                  {detectedPerson.reminders.map((item, index) => (
                    <li
                      key={index}
                      className="flex items-center gap-2 text-sm p-2 rounded bg-background/50"
                    >
                      <Package className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recentAlerts.map((alert, index) => (
            <AlertCard
              key={alert.id || (alert as any)._id || index}
              alert={alert}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
