import React from 'react';
import { Database, ShieldCheck, Terminal } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-sky-100 bg-white/80 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-x-2 gap-y-1">
            <span className="font-semibold text-slate-700">Dynamic Railway ETA Prediction</span>
            <span className="hidden sm:inline text-slate-300">•</span>
            <span>FastAPI &amp; Scikit-Learn Engine</span>
          </div>

          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-x-5 gap-y-2">
            <div className="flex items-center space-x-1.5 rounded-full bg-slate-50 px-2.5 py-1 border border-slate-200">
              <Database className="w-3.5 h-3.5 text-slate-500" />
              <span>JSONL Data Collection</span>
            </div>
            <div className="flex items-center space-x-1.5 rounded-full bg-emerald-50 px-2.5 py-1 border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Secure API Proxy</span>
            </div>
            <div className="flex items-center space-x-1.5 rounded-full bg-blue-50 px-2.5 py-1 border border-blue-200">
              <Terminal className="w-3.5 h-3.5 text-blue-500" />
              <span>Vite + React 19</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
