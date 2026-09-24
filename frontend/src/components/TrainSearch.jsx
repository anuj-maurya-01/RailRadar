import React from 'react';
import { Search, Loader2, ArrowRight } from 'lucide-react';

/**
 * Prominent search section for entering train number and querying the backend.
 * Responsive for mobile and desktop.
 */
export const TrainSearch = ({
  trainNumber,
  setTrainNumber,
  onSearch,
  loading = false,
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(String(trainNumber || '').trim());
    }
  };

  const handleChipClick = (num) => {
    const cleanNum = String(num || '').trim();
    setTrainNumber(cleanNum);
    if (onSearch) {
      onSearch(cleanNum);
    }
  };

  return (
    <div className="relative overflow-hidden rounded-[30px] border border-slate-200/80 bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 p-5 sm:p-6 shadow-[0_24px_60px_rgba(15,23,42,0.25)] rail-card">
      <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-r from-orange-500/20 via-sky-500/10 to-transparent" />
      <div className="relative">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-orange-300">Live rail status</p>
            <h2 className="text-lg sm:text-2xl font-black text-white tracking-tight mt-1">
              Track your train instantly
            </h2>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-400/30 bg-sky-500/10 px-3 py-1.5 text-[11px] font-semibold text-sky-100">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Live tracking active
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 min-w-0">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-sky-300">
                <Search className="w-5 h-5" />
              </div>
              <input
                id="train-number-input"
                type="text"
                inputMode="numeric"
                maxLength={10}
                disabled={loading}
                value={trainNumber}
                onChange={(e) => setTrainNumber(e.target.value)}
                placeholder="Search train number"
                className="w-full pl-11 pr-4 py-3.5 bg-white/95 border border-slate-200 rounded-2xl text-slate-900 placeholder-slate-400 text-sm focus:outline-none focus:ring-4 focus:ring-orange-500/20 focus:border-orange-400 transition-all font-mono shadow-inner disabled:opacity-60 disabled:cursor-not-allowed"
              />
            </div>

            <button
              id="search-train-button"
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 bg-gradient-to-r from-orange-500 to-amber-400 hover:from-orange-400 hover:to-amber-300 active:from-orange-600 active:to-amber-500 text-slate-900 font-bold text-sm rounded-2xl shadow-[0_12px_30px_rgba(249,115,22,0.35)] transition-all space-x-2 shrink-0 disabled:from-orange-400 disabled:to-amber-300 disabled:cursor-not-allowed cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <span>Search Train</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-200">
            <span className="font-semibold text-slate-100">Popular:</span>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleChipClick('11013')}
              className="px-2.5 py-1.5 rounded-full bg-white/5 text-slate-100 border border-slate-700 hover:border-orange-400/60 hover:bg-orange-500/10 font-mono transition-all disabled:opacity-50 cursor-pointer"
            >
              11013
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleChipClick('11014')}
              className="px-2.5 py-1.5 rounded-full bg-white/5 text-slate-100 border border-slate-700 hover:border-orange-400/60 hover:bg-orange-500/10 font-mono transition-all disabled:opacity-50 cursor-pointer"
            >
              11014
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => handleChipClick('12919')}
              className="px-2.5 py-1.5 rounded-full bg-white/5 text-slate-100 border border-slate-700 hover:border-orange-400/60 hover:bg-orange-500/10 font-mono transition-all disabled:opacity-50 cursor-pointer"
            >
              12919
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TrainSearch;
