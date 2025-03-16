export interface ServiceStatus {
  status: boolean;
  uptime_24h: number;
  uptime_7d: number;
  uptime_30d: number;
  last_updated: string;
}

export interface LogEntry {
  timestamp: string;
  message: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  error: string | null;
  password?: string;
}

export interface Config {
  uptimeCheckType: 'service' | 'web';
  serviceName?: string;
  webEndpointUrl?: string;
  logFilePath: string;
}