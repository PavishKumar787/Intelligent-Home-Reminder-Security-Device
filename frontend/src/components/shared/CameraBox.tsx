import React from 'react';
import { Video, VideoOff, Maximize2, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

interface CameraBoxProps {
  isLive?: boolean;
  detectedPerson?: {
    name: string;
    isKnown: boolean;
    confidence?: number;
  } | null;
  className?: string;
}

const CameraBox: React.FC<CameraBoxProps> = ({
  isLive = true,
  detectedPerson,
  className,
}) => {
  return (
    <div className={cn('glass-card rounded-xl overflow-hidden border border-border', className)}>
      {/* Camera Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-secondary/30">
        <div className="flex items-center gap-3">
          {isLive ? (
            <Video className="h-4 w-4 text-success" />
          ) : (
            <VideoOff className="h-4 w-4 text-muted-foreground" />
          )}
          <span className="font-medium text-sm">Live Camera Feed</span>
          {isLive && (
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className="text-xs text-success font-medium">LIVE</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* Camera Feed Area */}
      <div className="relative aspect-video bg-black overflow-hidden">
        {isLive ? (
          <img
            src="http://127.0.0.1:8000/video-feed"
            alt="Live Camera Feed"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-secondary to-background">
            <div className="text-center space-y-3">
              <div className="w-20 h-20 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
                <VideoOff className="h-8 w-8 text-muted-foreground" />
              </div>
              <p className="text-sm text-muted-foreground">Camera Offline</p>
            </div>
          </div>
        )}
        
        {/* Scan lines effect (only when live) */}
        {isLive && (
          <div className="absolute inset-0 pointer-events-none opacity-10">
            <div className="h-full w-full" style={{
              backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, hsl(var(--foreground) / 0.03) 2px, hsl(var(--foreground) / 0.03) 4px)'
            }} />
          </div>
        )}
        
        {/* Detection overlay */}
        {detectedPerson && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className={cn(
              'glass-card rounded-lg p-3 border animate-fade-in',
              detectedPerson.isKnown 
                ? 'border-success/50 bg-success/10' 
                : 'border-destructive/50 bg-destructive/10'
            )}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold',
                    detectedPerson.isKnown 
                      ? 'bg-success/20 text-success' 
                      : 'bg-destructive/20 text-destructive'
                  )}>
                    {detectedPerson.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{detectedPerson.name}</p>
                    <p className={cn(
                      'text-xs',
                      detectedPerson.isKnown ? 'text-success' : 'text-destructive'
                    )}>
                      {detectedPerson.isKnown ? 'Known User' : 'Unknown Person'}
                    </p>
                  </div>
                </div>
                <span className={cn(
                  'px-3 py-1 rounded-full text-xs font-semibold',
                  detectedPerson.isKnown 
                    ? 'bg-success text-success-foreground' 
                    : 'bg-destructive text-destructive-foreground'
                )}>
                  {detectedPerson.isKnown ? 'VERIFIED' : 'ALERT'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraBox;
