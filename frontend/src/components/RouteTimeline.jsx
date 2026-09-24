import React, { useMemo, useState, useRef, useEffect } from 'react';
import {
  CheckCircle2,
  Clock,
  Milestone,
  Flag,
  AlertCircle,
  CalendarClock,
  ArrowDownCircle,
  Maximize2,
  Minimize2,
  MapPin,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import {
  formatSafeText,
  formatDelayDisplay,
  formatTimeDisplay,
} from '../utils/formatters';

/**
 * Route & Station Timeline Component.
 * Space-efficient, interactive transit timeline:
 * - Constrained default max-height with smooth scrolling
 * - Jump-to-current position button
 * - Filter tabs (All Stops, Remaining, Passed)
 * - Collapsible passed stops group to reduce vertical scroll
 * - Compact, high-density row design
 */
export const RouteTimeline = ({ trainData }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filterTab, setFilterTab] = useState('all'); // 'all' | 'remaining' | 'passed'
  const [showPassedStops, setShowPassedStops] = useState(false);
  const currentRef = useRef(null);
  const containerRef = useRef(null);

  // 1. Resolve and classify all stations along the route
  const { stationsList, currentIndex, nextIndex, hasValidRoute } = useMemo(() => {
    const routeStations = trainData?.route?.stations;
    if (!Array.isArray(routeStations) || routeStations.length === 0) {
      return { stationsList: [], currentIndex: -1, nextIndex: -1, hasValidRoute: false };
    }

    const liveStatus = trainData?.live_status || {};
    const prediction = trainData?.prediction || {};
    const currentSeq = liveStatus.current_sequence;
    const currentCode = (liveStatus.current_station_code || '').trim().toUpperCase();
    const nextCode = (prediction.next_station_code || '').trim().toUpperCase();

    // Map each station object with standardized properties
    const stations = routeStations.map((stn, idx) => {
      const code = (stn.stationCode || stn.station_code || stn.code || '').trim();
      const name = (stn.stationName || stn.station_name || stn.name || '').trim();
      const seq = stn.sequence !== undefined && stn.sequence !== null ? Number(stn.sequence) : idx + 1;
      const distance = stn.distance !== undefined && stn.distance !== null ? Number(stn.distance) : null;

      return {
        ...stn,
        sequence: seq,
        code,
        name,
        distance,
      };
    });

    // Find current station index
    let matchedCurrentIdx = -1;

    // A. Match by sequence number if available
    if (currentSeq !== null && currentSeq !== undefined) {
      const numSeq = Number(currentSeq);
      matchedCurrentIdx = stations.findIndex((s) => s.sequence === numSeq);
    }

    // B. Match by stationCode if sequence did not match
    if (matchedCurrentIdx === -1 && currentCode) {
      matchedCurrentIdx = stations.findIndex(
        (s) => s.code && s.code.toUpperCase() === currentCode
      );
    }

    // C. Match by station name if code/sequence did not match
    if (matchedCurrentIdx === -1 && liveStatus.current_station_name) {
      const cleanName = liveStatus.current_station_name.trim().toUpperCase();
      matchedCurrentIdx = stations.findIndex(
        (s) => s.name && (s.name.toUpperCase().includes(cleanName) || cleanName.includes(s.name.toUpperCase()))
      );
    }

    // D. Fallback: If next_station is matched, current station may be the preceding one
    if (matchedCurrentIdx === -1 && (nextCode || prediction.next_station)) {
      const cleanNextName = (prediction.next_station || '').trim().toUpperCase();
      const matchedNextIdx = stations.findIndex(
        (s) =>
          (nextCode && s.code && s.code.toUpperCase() === nextCode) ||
          (cleanNextName && s.name && (s.name.toUpperCase().includes(cleanNextName) || cleanNextName.includes(s.name.toUpperCase())))
      );
      if (matchedNextIdx > 0) {
        matchedCurrentIdx = matchedNextIdx - 1;
      } else if (matchedNextIdx === 0) {
        matchedCurrentIdx = 0;
      }
    }

    // E. Default fallback: Ensure live position is ALWAYS highlighted
    if (matchedCurrentIdx === -1 && stations.length > 0) {
      matchedCurrentIdx = 0;
    }

    // Determine next station index
    let matchedNextIdx = -1;
    if (nextCode) {
      matchedNextIdx = stations.findIndex(
        (s) => s.code && s.code.toUpperCase() === nextCode
      );
    }
    if (matchedNextIdx === -1 && matchedCurrentIdx >= 0 && matchedCurrentIdx < stations.length - 1) {
      matchedNextIdx = matchedCurrentIdx + 1;
    }

    return {
      stationsList: stations,
      currentIndex: matchedCurrentIdx,
      nextIndex: matchedNextIdx,
      hasValidRoute: stations.length > 0,
    };
  }, [trainData]);

  // Jump to Current Station (scrolls container only, not the page)
  const scrollToCurrent = () => {
    if (currentRef.current && containerRef.current) {
      const container = containerRef.current;
      const target = currentRef.current;
      const targetOffset = target.offsetTop - container.offsetTop;
      container.scrollTo({
        top: Math.max(0, targetOffset - container.clientHeight / 2 + target.clientHeight / 2),
        behavior: 'smooth',
      });
    }
  };

  // Auto-scroll inside container only on mount or train change
  useEffect(() => {
    const timer = setTimeout(() => {
      scrollToCurrent();
    }, 250);
    return () => clearTimeout(timer);
  }, [currentIndex, filterTab]);

  // Route Unavailable Fallback
  if (!hasValidRoute) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
          <ArrowDownCircle className="w-5 h-5 text-slate-400" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">Route &amp; Station Timeline</h3>
        </div>

        <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl p-6 sm:p-8 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 rounded-full bg-slate-200/80 dark:bg-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-400 mx-auto mb-3">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h4 className="text-sm sm:text-base font-bold text-slate-800 dark:text-white">
            Route information is not available.
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 leading-relaxed">
            Detailed station timetable and intermediate checkpoint schedules are not exposed for this train service.
          </p>
        </div>
      </div>
    );
  }

  const liveStatus = trainData?.live_status || {};
  const prediction = trainData?.prediction || {};
  const lastIdx = stationsList.length - 1;

  const passedCount = currentIndex >= 0 ? currentIndex : 0;
  const remainingCount = Math.max(0, stationsList.length - (currentIndex >= 0 ? currentIndex : 0));

  // Determine filtered list based on tab
  const displayedStations = stationsList.filter((_, idx) => {
    if (filterTab === 'remaining') {
      return currentIndex < 0 || idx >= currentIndex;
    }
    if (filterTab === 'passed') {
      return currentIndex >= 0 && idx < currentIndex;
    }
    return true;
  });

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
      {/* Timeline Section Header */}
      <div className="px-4 sm:px-6 py-3 border-b border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2.5 bg-slate-50 dark:bg-slate-850">
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs shrink-0">
            <ArrowDownCircle className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center space-x-2">
              <h3 className="text-sm sm:text-base font-bold text-slate-900 dark:text-white tracking-tight truncate">
                Route &amp; Station Timeline
              </h3>
              <span className="px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-mono font-bold shrink-0">
                {stationsList.length} Stops
              </span>
            </div>
          </div>
        </div>

        {/* Action Controls & Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Filter Pills */}
          <div className="flex items-center bg-slate-200/70 dark:bg-slate-800 p-0.5 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => setFilterTab('all')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterTab === 'all'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setFilterTab('remaining')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterTab === 'remaining'
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
              }`}
            >
              Remaining ({remainingCount})
            </button>
            {passedCount > 0 && (
              <button
                type="button"
                onClick={() => setFilterTab('passed')}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  filterTab === 'passed'
                    ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs font-bold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
                }`}
              >
                Passed ({passedCount})
              </button>
            )}
          </div>

          {/* Jump to Live Position Button */}
          {currentIndex >= 0 && (
            <button
              type="button"
              onClick={scrollToCurrent}
              className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 text-xs font-bold hover:bg-blue-100 transition-colors"
              title="Jump to current live train position"
            >
              <MapPin className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
              <span className="hidden sm:inline">Jump to</span> Live
            </button>
          )}

          {/* Expand / Collapse Height Toggle */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 transition-colors"
            title={isExpanded ? 'Collapse timeline height' : 'Expand full timeline'}
            aria-label={isExpanded ? 'Collapse timeline height' : 'Expand full timeline'}
          >
            {isExpanded ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Timeline Stations List Container */}
      <div
        ref={containerRef}
        className={`p-3 sm:p-5 transition-all duration-200 ${
          isExpanded ? 'max-h-none' : 'max-h-[460px] overflow-y-auto custom-scrollbar'
        }`}
      >
        <div className="relative pl-5 sm:pl-7">
          {/* Continuous Vertical Connecting Spine Line */}
          <div
            className="absolute left-[13px] sm:[17px] top-3 bottom-3 w-0.5 bg-slate-200 dark:bg-slate-700"
            aria-hidden="true"
          />

          <div className="space-y-2">
            {displayedStations.map((station, mapIdx) => {
              const originalIdx = stationsList.findIndex(
                (s) => s.code === station.code && s.sequence === station.sequence
              );
              const idx = originalIdx >= 0 ? originalIdx : mapIdx;

              const isFirst = idx === 0;
              const isLast = idx === lastIdx;
              const isCurrent = idx === currentIndex;
              const isNext = idx === nextIndex;
              const isPassed = currentIndex >= 0 && idx < currentIndex;
              const isUpcoming = currentIndex >= 0 && idx > currentIndex && !isNext;

              // Timings
              const schedArr = formatTimeDisplay(
                station.scheduledArrival || station.scheduled_arrival
              );
              const schedDep = formatTimeDisplay(
                station.scheduledDeparture || station.scheduled_departure
              );
              const actArr = formatTimeDisplay(
                station.actualArrival || station.actual_arrival
              );
              const actDep = formatTimeDisplay(
                station.actualDeparture || station.actual_departure
              );

              // Next station expected timings
              const expectedArr = isNext
                ? formatTimeDisplay(prediction.expected_arrival || station.expectedArrival)
                : null;
              const expectedDep = isNext
                ? formatTimeDisplay(prediction.expected_departure || station.expectedDeparture)
                : null;

              // Terminus destination ETA
              const destEta = isLast
                ? formatTimeDisplay(prediction.destination_eta)
                : null;

              // Compact node & card styling
              let nodeStyle = 'bg-slate-300 dark:bg-slate-700 border-white dark:border-slate-900 text-slate-600 dark:text-slate-300';
              let cardStyle = 'bg-white dark:bg-slate-850 border-slate-200/80 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700';
              let badgeText = '';
              let badgeClass = '';

              if (isCurrent) {
                nodeStyle = 'bg-blue-600 border-white dark:border-slate-900 ring-3 ring-blue-100 dark:ring-blue-950 text-white animate-pulse';
                cardStyle = 'bg-blue-50/50 dark:bg-blue-950/30 border-blue-400 dark:border-blue-700 ring-1 ring-blue-300 dark:ring-blue-800 shadow-xs';
                badgeText = 'LIVE LOCATION';
                badgeClass = 'bg-blue-600 text-white font-bold';
              } else if (isNext) {
                nodeStyle = 'bg-amber-500 border-white dark:border-slate-900 ring-3 ring-amber-100 dark:ring-amber-950 text-white';
                cardStyle = 'bg-amber-50/30 dark:bg-amber-950/20 border-amber-300 dark:border-amber-700 shadow-xs';
                badgeText = 'NEXT STOP';
                badgeClass = 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-bold border border-amber-300 dark:border-amber-700';
              } else if (isLast) {
                nodeStyle = 'bg-rose-600 border-white dark:border-slate-900 text-white';
                cardStyle = 'bg-rose-50/20 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800';
                badgeText = 'TERMINUS';
                badgeClass = 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 font-bold border border-rose-200 dark:border-rose-800';
              } else if (isFirst) {
                nodeStyle = isPassed
                  ? 'bg-emerald-600 border-white dark:border-slate-900 text-white'
                  : 'bg-slate-700 dark:bg-slate-600 border-white dark:border-slate-900 text-white';
                badgeText = isPassed ? 'ORIGIN (PASSED)' : 'ORIGIN';
                badgeClass = isPassed
                  ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700';
              } else if (isPassed) {
                nodeStyle = 'bg-emerald-600 border-white dark:border-slate-900 text-white';
                cardStyle = 'bg-slate-50/50 dark:bg-slate-850/40 border-slate-200/50 dark:border-slate-800 opacity-75';
                badgeText = 'PASSED';
                badgeClass = 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400';
              }

              return (
                <React.Fragment key={`stn-${station.code || station.sequence}-${idx}`}>
                  <div
                    ref={isCurrent ? currentRef : null}
                    className="relative"
                  >
                    {/* Compact Timeline Node Point */}
                    <div
                      className={`absolute -left-[20px] sm:-left-[24px] top-2.5 w-6 h-6 sm:w-6 sm:h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold shadow-xs z-10 transition-transform ${nodeStyle}`}
                      aria-label={`${badgeText || 'Stop'}: ${station.name}`}
                    >
                      {isCurrent ? (
                        <span className="text-[11px]">🚆</span>
                      ) : isNext ? (
                        <Milestone className="w-3 h-3" />
                      ) : isLast ? (
                        <Flag className="w-3 h-3" />
                      ) : isPassed ? (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      ) : (
                        <span className="font-mono">{station.sequence}</span>
                      )}
                    </div>

                    {/* Streamlined Station Card */}
                    <div
                      className={`py-2 px-3 sm:px-4 rounded-lg border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 sm:gap-4 ${cardStyle}`}
                    >
                      {/* Left: Station Identity */}
                      <div className="min-w-0 flex items-center space-x-2 flex-wrap">
                        {badgeText && (
                          <span
                            className={`inline-flex items-center px-1.5 py-0.2 rounded text-[10px] font-semibold shrink-0 ${badgeClass}`}
                          >
                            {badgeText}
                          </span>
                        )}

                        <span className="text-xs font-mono text-slate-400 dark:text-slate-500 shrink-0">
                          #{station.sequence}
                        </span>

                        <h4
                          className={`text-sm sm:text-base font-bold tracking-tight truncate ${
                            isCurrent
                              ? 'text-blue-900 dark:text-blue-300 font-extrabold'
                              : isNext
                              ? 'text-amber-950 dark:text-amber-300 font-extrabold'
                              : 'text-slate-900 dark:text-white'
                          }`}
                          title={station.name}
                        >
                          {formatSafeText(station.name)}
                        </h4>

                        {station.code && (
                          <span className="px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-[11px] font-mono font-bold border border-slate-200 dark:border-slate-700 shrink-0">
                            {station.code}
                          </span>
                        )}

                        {station.distance !== null && (
                          <span className="text-[11px] text-slate-400 dark:text-slate-500 shrink-0 hidden md:inline">
                            • {station.distance} km
                          </span>
                        )}
                      </div>

                      {/* Right: Timetable & ETA Information */}
                      <div className="flex items-center space-x-2 sm:space-x-3 text-xs font-mono shrink-0 flex-wrap">
                        {/* Scheduled times */}
                        <div className="text-slate-500 dark:text-slate-400 flex items-center space-x-1.5">
                          <Clock className="w-3 h-3 text-slate-400 shrink-0" />
                          <span>
                            {schedArr !== 'Not available' ? schedArr : '--:--'}
                            <span className="mx-1 text-slate-300 dark:text-slate-600">/</span>
                            {schedDep !== 'Not available' ? schedDep : '--:--'}
                          </span>
                        </div>

                        {/* Special Status Timing Tags */}
                        {isCurrent && liveStatus.current_delay_minutes !== undefined && (
                          <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-950/80 text-blue-800 dark:text-blue-300 font-bold border border-blue-200 dark:border-blue-700">
                            {formatDelayDisplay(liveStatus.current_delay_minutes)}
                          </span>
                        )}

                        {isNext && expectedArr && expectedArr !== 'Not available' && (
                          <span className="px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-bold border border-amber-300 dark:border-amber-700">
                            Exp: {expectedArr}
                          </span>
                        )}

                        {isPassed && actArr && actArr !== 'Not available' && (
                          <span className="px-1.5 py-0.2 rounded bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 font-medium">
                            Act: {actArr}
                          </span>
                        )}

                        {isLast && destEta && destEta !== 'Not available' && (
                          <span className="px-2 py-0.5 rounded bg-emerald-600 text-white font-black shadow-xs">
                            ETA: {destEta}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer Summary Ribbon */}
      <div className="px-4 sm:px-6 py-2.5 bg-slate-50 dark:bg-slate-850 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center space-x-3">
          <span>
            Passed: <strong className="text-slate-700 dark:text-slate-200">{passedCount}</strong>
          </span>
          <span>•</span>
          <span>
            Remaining: <strong className="text-slate-700 dark:text-slate-200">{remainingCount}</strong>
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {!isExpanded && (
            <button
              type="button"
              onClick={() => setIsExpanded(true)}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Expand All
            </button>
          )}
          {isExpanded && (
            <button
              type="button"
              onClick={() => setIsExpanded(false)}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              Compact View
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RouteTimeline;
