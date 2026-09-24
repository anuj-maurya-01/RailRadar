import React, { useState, useEffect, useRef } from 'react';
import { Search, Loader2, ArrowRight, X, Sparkles, Navigation } from 'lucide-react';
import { getSearchSuggestions } from '../services/api';

/**
 * Hero Railway Search Component with Autocomplete Suggestions
 * Searches by train number, train name, or corridor station across Indian Railways dataset.
 */
export const TrainSearch = ({
  trainNumber,
  setTrainNumber,
  onSearch,
  loading = false,
  inputRef = null,
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const containerRef = useRef(null);
  const debounceTimerRef = useRef(null);

  // Debounced search suggestions lookup
  useEffect(() => {
    const q = String(trainNumber || '').trim();
    if (q.length < 2) {
      setSuggestions([]);
      setLoadingSuggestions(false);
      return;
    }

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(async () => {
      try {
        setLoadingSuggestions(true);
        const data = await getSearchSuggestions(q);
        if (data && Array.isArray(data.results)) {
          setSuggestions(data.results);
          setShowSuggestions(true);
        }
      } catch (err) {
        console.warn('Autocomplete lookup hiccup:', err.message);
      } finally {
        setLoadingSuggestions(false);
      }
    }, 220);

    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, [trainNumber]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    if (onSearch) {
      onSearch(String(trainNumber || '').trim());
    }
  };

  const handleSelectSuggestion = (item) => {
    setTrainNumber(item.train_number);
    setShowSuggestions(false);
    if (onSearch) {
      onSearch(item.train_number);
    }
  };

  const handleChipClick = (num) => {
    const cleanNum = String(num || '').trim();
    setTrainNumber(cleanNum);
    setShowSuggestions(false);
    if (onSearch) {
      onSearch(cleanNum);
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative rounded-2xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 p-5 sm:p-6 shadow-xs transition-colors duration-200"
    >
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-4">
          <p className="text-[11px] font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
            Real-Time Railway Intelligence
          </p>
          <h2 className="text-xl sm:text-2xl font-extrabold text-slate-950 dark:text-white tracking-tight mt-0.5">
            Track Any Train in India
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Live satellite telemetry, station checkpoints, and ML delay forecasting
          </p>
        </div>

        {/* Large Rounded Search Input */}
        <form onSubmit={handleSubmit} className="relative">
          <div className="relative flex flex-col sm:flex-row gap-2.5">
            <div className="relative flex-1 min-w-0">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 dark:text-slate-500">
                <Search className="w-5 h-5" />
              </div>

              <input
                ref={inputRef}
                id="train-number-input"
                type="text"
                maxLength={20}
                disabled={loading}
                value={trainNumber}
                onFocus={() => {
                  if (suggestions.length > 0) setShowSuggestions(true);
                }}
                onChange={(e) => setTrainNumber(e.target.value)}
                placeholder="Search train number, train name, or corridor station..."
                className="w-full pl-11 pr-10 py-3.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 text-sm focus:outline-none focus:ring-3 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 transition shadow-2xs font-sans"
              />

              {trainNumber && (
                <button
                  type="button"
                  onClick={() => {
                    setTrainNumber('');
                    setSuggestions([]);
                    setShowSuggestions(false);
                  }}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            <button
              id="search-train-button"
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto inline-flex items-center justify-center px-6 py-3.5 bg-slate-900 hover:bg-slate-800 active:bg-black dark:bg-blue-600 dark:hover:bg-blue-500 text-white font-semibold text-sm rounded-xl shadow-xs transition space-x-2 shrink-0 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Tracking...</span>
                </>
              ) : (
                <>
                  <span>Track Train</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

          {/* Autocomplete Suggestions Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 z-30 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden divide-y divide-slate-100 dark:divide-slate-800 animate-in fade-in-50 duration-150">
              <div className="px-3.5 py-2 bg-slate-50 dark:bg-slate-800/50 text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center justify-between">
                <span>Matching Trains ({suggestions.length})</span>
                <span className="text-[10px] text-slate-400">Click to inspect</span>
              </div>

              {suggestions.map((item) => (
                <div
                  key={item.train_number}
                  onMouseDown={() => handleSelectSuggestion(item)}
                  className="p-3 hover:bg-slate-50 dark:hover:bg-slate-800/80 cursor-pointer flex items-center justify-between gap-3 transition"
                >
                  <div className="flex items-center space-x-3 min-w-0">
                    <span className="font-mono font-bold text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 shrink-0">
                      {item.train_number}
                    </span>
                    <div className="min-w-0">
                      <div className="font-semibold text-xs text-slate-900 dark:text-white truncate">
                        {item.train_name}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">
                        {item.route}
                      </div>
                    </div>
                  </div>

                  <span className="text-[11px] text-blue-600 dark:text-blue-400 font-medium shrink-0">
                    Select →
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Popular Train Chips */}
          <div className="mt-3.5 flex flex-wrap items-center gap-2 text-xs">
            <span className="font-medium text-slate-400 dark:text-slate-500 text-[11px]">
              Popular Corridors:
            </span>
            {[
              { num: '11013', name: 'Coimbatore Exp' },
              { num: '11014', name: 'LTT Exp' },
              { num: '12919', name: 'Malwa Exp' },
              { num: '12841', name: 'Coromandel' },
              { num: '12626', name: 'Kerala Exp' },
            ].map((chip) => (
              <button
                key={chip.num}
                type="button"
                disabled={loading}
                onClick={() => handleChipClick(chip.num)}
                className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700/80 transition disabled:opacity-50 cursor-pointer"
              >
                <span className="font-mono font-bold text-[11px] text-slate-900 dark:text-white">
                  {chip.num}
                </span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 hidden sm:inline">
                  {chip.name}
                </span>
              </button>
            ))}
          </div>
        </form>
      </div>
    </div>
  );
};

export default TrainSearch;
