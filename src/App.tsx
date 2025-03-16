import React, { useState, useEffect, useCallback } from 'react';
import { LoginForm } from './components/LoginForm';
import { StatusIndicator } from './components/StatusIndicator';
import { LogViewer } from './components/LogViewer';
import { LoadingScreen } from './components/LoadingScreen';
import { AuthState, ServiceStatus, LogEntry } from './types';

function App() {
  const [auth, setAuth] = useState<AuthState>({
    isAuthenticated: false,
    error: null,
    password: ''
  });
  const [status, setStatus] = useState<ServiceStatus | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const connectWebSocket = useCallback(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws`;
    const socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status) {
        setStatus(data.status);
        setIsLoading(false);
      }
      if (data.logs) setLogs(data.logs);
    };

    socket.onclose = () => {
      setTimeout(connectWebSocket, 1000);
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    if (auth.isAuthenticated) {
      connectWebSocket();
    }
    return () => {
      if (ws) ws.close();
    };
  }, [auth.isAuthenticated, connectWebSocket]);

  const handleLogin = async (password: string) => {
    try {
      const response = await fetch('/api/auth', {
        method: 'GET',
        headers: {
          'Authorization': `Basic ${btoa(`:${password}`)}`,
        },
      });

      if (response.ok) {
        setAuth({ isAuthenticated: true, error: null, password });
      } else {
        setAuth({ isAuthenticated: false, error: 'Invalid password', password: '' });
      }
    } catch (error) {
      setAuth({ isAuthenticated: false, error: 'Authentication failed', password: '' });
    }
  };

  if (!auth.isAuthenticated) {
    return <LoginForm onLogin={handleLogin} error={auth.error} />;
  }

  if (isLoading || !status) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
            YugoSM Dashboard
          </h1>
        </div>
        <StatusIndicator status={status} />
        <LogViewer logs={logs} />
      </div>
    </div>
  );
}

export default App;