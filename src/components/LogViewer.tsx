import { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Terminal } from 'lucide-react';
import { LogEntry } from '../types';

interface LogViewerProps {
  logs: LogEntry[];
}

export function LogViewer({ logs }: LogViewerProps) {
  const [autoScroll, setAutoScroll] = useState(true);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-lg border shadow-lg p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Terminal className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold text-card-foreground">Service Logs</h2>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded bg-accent border-accent text-blue-400 focus:ring-offset-background"
            />
            <span className="text-sm text-muted-foreground">Auto-scroll</span>
          </label>
        </div>
      </div>

      <div
        ref={logContainerRef}
        className="bg-muted rounded-lg p-4 h-96 overflow-auto font-mono text-sm"
      >
        {logs.map((log, index) => (
          <div key={index} className="text-muted-foreground">
            <span className="text-blue-400">{log.timestamp}</span> {log.message}
          </div>
        ))}
      </div>
    </motion.div>
  );
}