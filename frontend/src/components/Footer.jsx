import React from 'react';
import { Database, ShieldCheck, Cpu } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-slate-200/90 dark:border-slate-800 bg-white/90 dark:bg-slate-950/90 backdrop-blur-sm transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400 text-center sm:text-left">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-x-2 gap-y-1">
            <span className="font-bold text-slate-800 dark:text-slate-200">YatriRail</span>
            <span className="hidden sm:inline text-slate-300 dark:text-slate-600">•</span>
            <span>Live Indian Railway Intelligence &amp; ML Arrival Prediction</span>
          </div>

          <div className="flex flex-wrap items-center justify-center sm:justify-end gap-x-4 gap-y-2">
            <div className="flex items-center space-x-1.5 rounded-full bg-slate-50 dark:bg-slate-900 px-2.5 py-1 border border-slate-200 dark:border-slate-800 text-[11px]">
              <Cpu className="w-3.5 h-3.5 text-blue-500" />
              <span>HistGradientBoosting ML Engine</span>
            </div>
            <div className="flex items-center space-x-1.5 rounded-full bg-slate-50 dark:bg-slate-900 px-2.5 py-1 border border-slate-200 dark:border-slate-800 text-[11px]">
              <Database className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
              <span>Dataset_1 Route Telemetry</span>
            </div>
            <div className="flex items-center space-x-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/40 px-2.5 py-1 border border-emerald-200 dark:border-emerald-800/60 text-emerald-700 dark:text-emerald-300 text-[11px]">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
              <span>Secure Railway Proxy</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
