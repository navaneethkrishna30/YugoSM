import { motion } from 'framer-motion';
import { Clock, TrendingUp } from 'lucide-react';
import { ServiceStatus } from '../types';
import { RelativeTime } from './RelativeTime';

interface StatusIndicatorProps {
  status: ServiceStatus;
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-lg border shadow-lg p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-card-foreground">Service Status</h2>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-muted-foreground">
            <RelativeTime timestamp={status.last_updated} />
          </span>
        </div>
      </div>

      <div className="flex flex-col space-y-2 mb-6">
        <div className="flex items-center space-x-2">
          <div
            className={`w-4 h-4 rounded-full ${
              status.status ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-lg font-medium text-card-foreground">
            {status.status ? 'Running' : 'Stopped'}
          </span>
        </div>
        
        <div className="text-sm text-muted-foreground">
          {status.check_type === 'endpoint' ? (
            <span>Monitoring health check API of Service</span>
          ) : (
            <span>Monitoring Service</span>
          )}
        </div>
        
        {status.last_error && !status.status && (
          <div className="text-sm text-red-500">
            Error: {status.last_error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-blue-400" />
            <p className="text-sm text-muted-foreground">24h Uptime</p>
          </div>
          <p className="text-2xl font-bold text-card-foreground">
            {status.uptime_24h.toFixed(1)}%
          </p>
        </div>
        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            <p className="text-sm text-muted-foreground">7d Uptime</p>
          </div>
          <p className="text-2xl font-bold text-card-foreground">
            {status.uptime_7d.toFixed(1)}%
          </p>
        </div>
        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            <p className="text-sm text-muted-foreground">30d Uptime</p>
          </div>
          <p className="text-2xl font-bold text-card-foreground">
            {status.uptime_30d.toFixed(1)}%
          </p>
        </div>
      </div>
    </motion.div>
  );
}