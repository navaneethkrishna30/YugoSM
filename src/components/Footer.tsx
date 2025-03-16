import React from 'react';
import { Github, Twitter, Linkedin, Code2 } from 'lucide-react';

export function Footer() {
  return (
    <footer className="py-6 border-t">
      <div className="max-w-6xl mx-auto px-6 flex flex-col items-center space-y-4">
        <div className="flex items-center space-x-6">
          <a
            href="https://github.com/navaneethk30/yugosm"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-blue-400 flex items-center space-x-2"
          >
            <Code2 className="w-5 h-5" />
          </a>
          <a
            href="https://github.com/navaneethkrishna30"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-blue-400"
          >
            <Github className="w-5 h-5" />
          </a>
          <a
            href="https://x.com/navaneethk30"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-blue-400"
          >
            <Twitter className="w-5 h-5" />
          </a>
          <a
            href="https://linkedin.com/in/navaneethkrishnamudumba"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-blue-400"
          >
            <Linkedin className="w-5 h-5" />
          </a>
        </div>
        <div className="text-sm text-muted-foreground">
          Built with ❤️ by Navaneeth Krishna
        </div>
      </div>
    </footer>
  );
} 