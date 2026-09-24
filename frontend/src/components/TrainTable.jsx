import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ChevronLeft, ChevronRight, Eye, Train as TrainIcon, ArrowRight, Clock } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { formatDelayDisplay, formatSpeed } from '../utils/formatters';

const ITEMS_PER_PAGE = 6;

/**
 * Professional Compact Live Trains Table
 * Replaces the long vertical list with an interactive, filterable, sortable, and paginated control table.
 */
export const TrainTable = ({
  trains = [],
  selectedTrainNumber = null,
  onSelectTrain = () => {},
  loading = false,
  activeFilter = 'all',
  onFilterChange = () => {},
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('delay_desc');
  const [currentPage, setCurrentPage] = useState(1);

  // 1. Filter by status and search term
  const filteredTrains = useMemo(() => {
    return trains.filter((train) => {
      // Status filter
      if (activeFilter === 'on_time') {
        if ((train.delay_minutes || 0) > 5) return false;
      } else if (activeFilter === 'delayed') {
        if ((train.delay_minutes || 0) <= 5) return false;
      } else if (activeFilter === 'cancelled') {
        if (train.status !== 'cancelled') return false;
      }

      // Search term filter
      if (searchTerm.trim()) {
        const q = searchTerm.toLowerCase().trim();
        const num = String(train.train_number || '').toLowerCase();
        const name = String(train.train_name || '').toLowerCase();
        const src = String(train.source || '').toLowerCase();
        const dst = String(train.destination || '').toLowerCase();
        const loc = String(train.current_station_name || '').toLowerCase();

        return (
          num.includes(q) ||
          name.includes(q) ||
          src.includes(q) ||
          dst.includes(q) ||
          loc.includes(q)
        );
      }

      return true;
    });
  }, [trains, activeFilter, searchTerm]);

  // 2. Sort
  const sortedTrains = useMemo(() => {
    return [...filteredTrains].sort((a, b) => {
      if (sortBy === 'delay_desc') {
        return (b.delay_minutes || 0) - (a.delay_minutes || 0);
      } else if (sortBy === 'delay_asc') {
        return (a.delay_minutes || 0) - (b.delay_minutes || 0);
      } else if (sortBy === 'train_num') {
        return String(a.train_number).localeCompare(String(b.train_number));
      } else if (sortBy === 'name') {
        return String(a.train_name).localeCompare(String(b.train_name));
      }
      return 0;
    });
  }, [filteredTrains, sortBy]);

  // 3. Paginate
  const totalPages = Math.max(1, Math.ceil(sortedTrains.length / ITEMS_PER_PAGE));
  const validCurrentPage = Math.min(currentPage, totalPages);
  const paginatedTrains = useMemo(() => {
    const start = (validCurrentPage - 1) * ITEMS_PER_PAGE;
    return sortedTrains.slice(start, start + ITEMS_PER_PAGE);
  }, [sortedTrains, validCurrentPage]);

  // Counts for filter pills
  const counts = useMemo(() => {
    const onTime = trains.filter((t) => (t.delay_minutes || 0) <= 5).length;
    const delayed = trains.filter((t) => (t.delay_minutes || 0) > 5).length;
    const cancelled = trains.filter((t) => t.status === 'cancelled').length;
    return { all: trains.length, on_time: onTime, delayed, cancelled };
  }, [trains]);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs overflow-hidden">
      {/* Table Header Controls */}
      <div className="p-4 sm:p-5 border-b border-slate-100 dark:border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <TrainIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span>LIVE TRAINS</span>
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Real-time monitoring across major express and superfast corridors
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            <button
              type="button"
              onClick={() => {
                onFilterChange('all');
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
                activeFilter === 'all'
                  ? 'bg-slate-900 text-white dark:bg-blue-600 shadow-xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              All ({counts.all})
            </button>
            <button
              type="button"
              onClick={() => {
                onFilterChange('on_time');
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
                activeFilter === 'on_time'
                  ? 'bg-emerald-600 text-white shadow-xs'
                  : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/40'
              }`}
            >
              🟢 On Time ({counts.on_time})
            </button>
            <button
              type="button"
              onClick={() => {
                onFilterChange('delayed');
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
                activeFilter === 'delayed'
                  ? 'bg-amber-600 text-white shadow-xs'
                  : 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900/40'
              }`}
            >
              🟠 Delayed ({counts.delayed})
            </button>
            <button
              type="button"
              onClick={() => {
                onFilterChange('cancelled');
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
                activeFilter === 'cancelled'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 hover:bg-rose-100 dark:hover:bg-rose-900/40'
              }`}
            >
              🔴 Cancelled ({counts.cancelled})
            </button>
          </div>
        </div>

        {/* Search within table & Sorting */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search within trains..."
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto justify-end text-xs">
            <span className="text-slate-400 dark:text-slate-500 text-[11px] font-medium flex items-center gap-1">
              <ArrowUpDown className="w-3.5 h-3.5" />
              <span>Sort:</span>
            </span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 cursor-pointer"
            >
              <option value="delay_desc">Delay (Highest first)</option>
              <option value="delay_asc">Delay (Lowest first)</option>
              <option value="train_num">Train Number</option>
              <option value="name">Train Name</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table Content */}
      {loading ? (
        <div className="p-8 space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-14 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : sortedTrains.length === 0 ? (
        <div className="p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
            <Search className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">No trains match your filters</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
            Try resetting the status filter or clearing your search query.
          </p>
          <button
            type="button"
            onClick={() => {
              onFilterChange('all');
              setSearchTerm('');
            }}
            className="mt-4 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div>

          {/* Mobile Responsive Cards View (visible on < sm) */}
          <div className="sm:hidden divide-y divide-slate-100 dark:divide-slate-800">
            {paginatedTrains.map((train) => {
              const isSelected = String(selectedTrainNumber) === String(train.train_number);
              const delay = Number(train.delay_minutes || 0);

              return (
                <div
                  key={train.train_number}
                  onClick={() => onSelectTrain(train.train_number, train)}
                  className={`p-4 transition-colors cursor-pointer space-y-2.5 ${
                    isSelected
                      ? 'bg-blue-50/80 dark:bg-blue-950/40'
                      : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center space-x-2 min-w-0">
                      <span className="font-mono font-bold text-xs px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 shrink-0">
                        #{train.train_number}
                      </span>
                      <h4 className="font-bold text-xs text-slate-900 dark:text-white truncate">
                        {train.train_name}
                      </h4>
                    </div>

                    <StatusBadge status={train.status} delayMinutes={delay} size="sm" />
                  </div>

                  <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center space-x-1.5 font-medium">
                    <span className="truncate">{train.source}</span>
                    <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                    <span className="truncate">{train.destination}</span>
                  </div>

                  <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-100 dark:border-slate-800/60">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Current Location</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200 text-xs">
                        {train.current_station_name}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Delay</span>
                      <span
                        className={`font-mono font-bold ${
                          delay > 5
                            ? 'text-amber-600 dark:text-amber-400'
                            : 'text-emerald-600 dark:text-emerald-400'
                        }`}
                      >
                        {formatDelayDisplay(delay)}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Desktop Table View (visible on >= sm) */}
          <div className="hidden sm:block overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/70 dark:bg-slate-800/50 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider border-b border-slate-100 dark:border-slate-800">
                  <th className="py-3 px-4 sm:px-6">Train</th>
                  <th className="py-3 px-4 hidden md:table-cell">Route</th>
                  <th className="py-3 px-4">Current Location</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Delay</th>
                  <th className="py-3 px-4 sm:px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 text-xs">
                {paginatedTrains.map((train) => {
                  const isSelected = String(selectedTrainNumber) === String(train.train_number);
                  const delay = Number(train.delay_minutes || 0);

                  return (
                    <tr
                      key={train.train_number}
                      onClick={() => onSelectTrain(train.train_number, train)}
                      className={`group cursor-pointer transition-colors duration-150 ${
                        isSelected
                          ? 'bg-blue-50/80 dark:bg-blue-950/40'
                          : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'
                      }`}
                    >
                      {/* Train Info */}
                      <td className="py-3.5 px-4 sm:px-6">
                        <div className="flex items-center space-x-3">
                          <span className="font-mono font-bold text-xs px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/60 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
                            {train.train_number}
                          </span>
                          <div>
                            <div className="font-semibold text-slate-900 dark:text-white leading-tight">
                              {train.train_name}
                            </div>
                            <div className="text-[11px] text-slate-400 md:hidden mt-0.5 truncate max-w-[180px]">
                              {train.source} → {train.destination}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Route (Desktop) */}
                      <td className="py-3.5 px-4 hidden md:table-cell text-slate-600 dark:text-slate-300">
                        <div className="flex items-center space-x-1.5 text-xs truncate max-w-xs">
                          <span className="truncate">{train.source}</span>
                          <ArrowRight className="w-3 h-3 text-slate-400 shrink-0" />
                          <span className="truncate">{train.destination}</span>
                        </div>
                      </td>

                      {/* Current Location */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-slate-800 dark:text-slate-200">
                          {train.current_station_name}
                        </div>
                        {train.speed_kmh > 0 && (
                          <div className="text-[11px] text-slate-400 font-mono">
                            {formatSpeed(train.speed_kmh)}
                          </div>
                        )}
                      </td>

                      {/* Status Badge */}
                      <td className="py-3.5 px-4">
                        <StatusBadge status={train.status} delayMinutes={delay} size="sm" />
                      </td>

                      {/* Delay */}
                      <td className="py-3.5 px-4">
                        <span
                          className={`font-mono font-bold ${
                            delay > 5
                              ? 'text-amber-600 dark:text-amber-400'
                              : 'text-emerald-600 dark:text-emerald-400'
                          }`}
                        >
                          {formatDelayDisplay(delay)}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-3.5 px-4 sm:px-6 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectTrain(train.train_number, train);
                          }}
                          className={`inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                            isSelected
                              ? 'bg-blue-600 text-white shadow-2xs'
                              : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200'
                          }`}
                        >
                          <span>{isSelected ? 'Viewing' : 'View'}</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}




      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div className="p-3.5 sm:p-4 bg-slate-50/60 dark:bg-slate-800/40 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
          <div className="text-slate-500 dark:text-slate-400">
            Showing{' '}
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {(validCurrentPage - 1) * ITEMS_PER_PAGE + 1}
            </span>{' '}
            to{' '}
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {Math.min(validCurrentPage * ITEMS_PER_PAGE, sortedTrains.length)}
            </span>{' '}
            of{' '}
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {sortedTrains.length}
            </span>{' '}
            trains
          </div>

          <div className="flex items-center space-x-1.5">
            <button
              type="button"
              disabled={validCurrentPage === 1}
              onClick={() => handlePageChange(validCurrentPage - 1)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="px-2 font-medium text-slate-600 dark:text-slate-400">
              Page {validCurrentPage} of {totalPages}
            </span>

            <button
              type="button"
              disabled={validCurrentPage === totalPages}
              onClick={() => handlePageChange(validCurrentPage + 1)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

    </div>
  );
};

export default TrainTable;
