import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export function LoadingScreen() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center space-y-4"
      >
        <Loader2 className="w-12 h-12 text-blue-400 animate-spin" />
        <h2 className="text-xl font-semibold text-card-foreground">
          Loading dashboard...
        </h2>
      </motion.div>
    </div>
  );
} 