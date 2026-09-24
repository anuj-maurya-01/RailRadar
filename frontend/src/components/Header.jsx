import React from 'react';
import { Train, Activity, Cpu, MapPinned } from 'lucide-react';

export const Header = () => {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-slate-950/95 backdrop-blur-xl shadow-[0_12px_30px_rgba(15,23,42,0.28)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18 py-3">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-orange-500 via-orange-400 to-amber-300 flex items-center justify-center text-white shadow-[0_12px_25px_rgba(249,115,22,0.35)] shrink-0 ring-4 ring-orange-500/20">
              <Train className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="font-black text-lg text-white tracking-tight">RailRadar</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-orange-500/15 text-orange-200 border border-orange-400/25">
                  LIVE
                </span>
              </div>
              <p className="text-[11px] text-slate-300 hidden sm:block tracking-[0.14em] uppercase">
                Train tracker & ETA update
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <div className="hidden md:flex items-center space-x-1.5 text-slate-200 bg-slate-800/80 px-2.5 py-1.5 rounded-full border border-slate-700 shadow-sm">
              <MapPinned className="w-3.5 h-3.5 text-sky-400" />
              <span className="font-medium">Route Map</span>
            </div>
            <div className="hidden sm:flex items-center space-x-1.5 text-slate-100 bg-slate-800/80 px-2.5 py-1.5 rounded-full border border-slate-700 shadow-sm">
              <Cpu className="w-3.5 h-3.5 text-violet-400" />
              <span className="font-medium">AI ETA</span>
            </div>
            <div className="flex items-center space-x-1.5 text-emerald-200 bg-emerald-500/10 px-2.5 py-1.5 rounded-full border border-emerald-400/30 shadow-sm">
              <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span className="font-medium">Live</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
