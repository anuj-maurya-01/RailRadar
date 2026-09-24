import React, { useMemo } from 'react';
import {
  CheckCircle2,
  Clock,
  Milestone,
  Flag,
  AlertCircle,
  CalendarClock,
  ArrowDownCircle,
} from 'lucide-react';
import {
  formatSafeText,
  formatDelayDisplay,
  formatTimeDisplay,
} from '../utils/formatters';

/**
 * Route & Station Timeline Component.
 * Displays the complete train journey as an accessible, responsive vertical timeline
 * visually distinguishing Completed, Current, Next, Upcoming, and Destination stops.
 */
export const RouteTimeline = ({ trainData }) => {
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

    // C. Fallback: If next_station is matched, current station may be the preceding one
    if (matchedCurrentIdx === -1 && nextCode) {
      const matchedNextIdx = stations.findIndex(
        (s) => s.code && s.code.toUpperCase() === nextCode
      );
      if (matchedNextIdx > 0) {
        matchedCurrentIdx = matchedNextIdx - 1;
      }
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

  // Requirement 11: Route Unavailable Fallback
  if (!hasValidRoute) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-100 mb-4">
          <ArrowDownCircle className="w-5 h-5 text-slate-400" />
          <h3 className="text-base font-bold text-slate-900">Route &amp; Station Timeline</h3>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 sm:p-8 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 rounded-full bg-slate-200/80 flex items-center justify-center text-slate-500 mx-auto mb-3">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h4 className="text-sm sm:text-base font-bold text-slate-800">
            Route information is not available.
          </h4>
          <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
            Detailed station timetable and intermediate checkpoint schedules are not exposed for this train service.
          </p>
        </div>
      </div>
    );
  }

  const liveStatus = trainData?.live_status || {};
  const prediction = trainData?.prediction || {};
  const lastIdx = stationsList.length - 1;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Timeline Section Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 bg-slate-50">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <ArrowDownCircle className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">
              Route &amp; Station Timeline
            </h3>
            <p className="text-xs text-slate-500">
              {stationsList.length} Scheduled Station Checkpoints
            </p>
          </div>
        </div>

        {/* Status Legend */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-slate-600">
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
            <CheckCircle2 className="w-3 h-3 text-slate-400" />
            <span>Passed</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold">
            <span>🚆</span>
            <span>Current Location</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-semibold">
            <Milestone className="w-3 h-3 text-amber-600" />
            <span>Next Stop</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 font-semibold">
            <Flag className="w-3 h-3 text-rose-600" />
            <span>Terminus</span>
          </div>
        </div>
      </div>

      {/* Timeline Stations List */}
      <div className="p-4 sm:p-6 lg:p-8">
        <div className="relative pl-6 sm:pl-8">
          {/* Continuous Vertical Connecting Spine Line */}
          <div
            className="absolute left-[15px] sm:left-[19px] top-4 bottom-4 w-0.5 bg-slate-200"
            aria-hidden="true"
          />

          <div className="space-y-6">
            {stationsList.map((station, idx) => {
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

              // Node icon & spine styling
              let nodeStyle = 'bg-slate-300 border-white text-slate-600';
              let cardStyle = 'bg-white border-slate-200/80 hover:border-slate-300';
              let badgeText = 'Scheduled Stop';
              let badgeClass = 'bg-slate-100 text-slate-600 border-slate-200';

              if (isCurrent) {
                nodeStyle = 'bg-blue-600 border-white ring-4 ring-blue-100 text-white animate-pulse';
                cardStyle = 'bg-blue-50/40 border-blue-300 shadow-xs ring-1 ring-blue-200';
                badgeText = 'CURRENT LOCATION';
                badgeClass = 'bg-blue-600 text-white font-bold border-blue-600';
              } else if (isNext) {
                nodeStyle = 'bg-amber-500 border-white ring-4 ring-amber-100 text-white';
                cardStyle = 'bg-amber-50/30 border-amber-300 shadow-xs';
                badgeText = 'NEXT STOP';
                badgeClass = 'bg-amber-100 text-amber-800 font-bold border-amber-300';
              } else if (isLast) {
                nodeStyle = 'bg-rose-600 border-white ring-2 ring-rose-100 text-white';
                cardStyle = 'bg-rose-50/30 border-rose-200';
                badgeText = 'TERMINUS DESTINATION';
                badgeClass = 'bg-rose-100 text-rose-800 font-bold border-rose-200';
              } else if (isFirst) {
                nodeStyle = isPassed
                  ? 'bg-emerald-600 border-white text-white'
                  : 'bg-slate-700 border-white text-white';
                badgeText = isPassed ? 'PASSED SOURCE' : 'ORIGIN SOURCE';
                badgeClass = isPassed
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-slate-100 text-slate-700 border-slate-200';
              } else if (isPassed) {
                nodeStyle = 'bg-emerald-600 border-white text-white';
                cardStyle = 'bg-slate-50/60 border-slate-200/60 opacity-80';
                badgeText = 'PASSED';
                badgeClass = 'bg-slate-100 text-slate-500 border-slate-200';
              } else if (isUpcoming) {
                badgeText = 'UPCOMING';
                badgeClass = 'bg-slate-50 text-slate-600 border-slate-200';
              }

              return (
                <div key={`stn-${station.code || station.sequence}-${idx}`} className="relative">
                  {/* Timeline Node Point on the Spine */}
                  <div
                    className={`absolute -left-[23px] sm:-left-[27px] top-3 w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold shadow-xs z-10 transition-transform ${nodeStyle}`}
                    aria-label={`${badgeText}: ${station.name}`}
                  >
                    {isCurrent ? (
                      <span className="text-sm">🚆</span>
                    ) : isNext ? (
                      <Milestone className="w-3.5 h-3.5" />
                    ) : isLast ? (
                      <Flag className="w-3.5 h-3.5" />
                    ) : isPassed ? (
                      <CheckCircle2 className="w-4 h-4" />
                    ) : (
                      <span className="text-[10px] font-mono">{station.sequence}</span>
                    )}
                  </div>

                  {/* Station Information Card */}
                  <div className={`p-4 rounded-xl border transition-all ${cardStyle}`}>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      {/* Station Identity */}
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                          {/* Station Status Badge */}
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${badgeClass}`}
                          >
                            {badgeText}
                          </span>

                          {/* Station Sequence */}
                          <span className="text-xs font-mono text-slate-400">
                            Stop #{station.sequence}
                          </span>

                          {/* Route Distance if available */}
                          {station.distance !== null && (
                            <span className="text-xs text-slate-400">
                              • {station.distance} km
                            </span>
                          )}
                        </div>

                        {/* Station Name & Code (Graceful Long Name Wrapping) */}
                        <div className="mt-1.5 flex items-baseline space-x-2 flex-wrap">
                          <h4
                            className={`text-base sm:text-lg font-bold tracking-tight break-words ${
                              isCurrent
                                ? 'text-blue-900 font-extrabold'
                                : isNext
                                ? 'text-amber-950 font-extrabold'
                                : 'text-slate-900'
                            }`}
                          >
                            {formatSafeText(station.name)}
                          </h4>
                          {station.code && (
                            <span className="px-1.5 py-0.2 rounded bg-slate-100 text-slate-700 text-xs font-mono font-bold border border-slate-200">
                              {station.code}
                            </span>
                          )}
                        </div>

                        {/* Live Current Station Meta */}
                        {isCurrent && (
                          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
                            {liveStatus.status && (
                              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-medium capitalize">
                                Status: {liveStatus.status}
                              </span>
                            )}
                            <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-800 font-medium border border-amber-200">
                              LIVE DELAY: {formatDelayDisplay(liveStatus.current_delay_minutes)}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* Station Timetable & Status Timing Block */}
                      <div className="shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                        <div className="grid grid-cols-2 sm:flex sm:items-center gap-3 sm:gap-4 text-xs font-mono">
                          {/* Arrival Timing */}
                          <div className="bg-white/80 p-2 rounded-lg border border-slate-200/80 min-w-[105px]">
                            <div className="text-[10px] font-sans font-semibold text-slate-400 uppercase flex items-center space-x-1">
                              <CalendarClock className="w-3 h-3 text-slate-400" />
                              <span>Arrival</span>
                            </div>

                            {/* Scheduled */}
                            {schedArr !== 'Not available' && (
                              <div className="text-slate-700 font-medium mt-0.5">
                                <span className="text-[10px] text-slate-400 font-sans mr-1">Sch:</span>
                                <span>{schedArr}</span>
                              </div>
                            )}

                            {/* Next Station Expected Arrival */}
                            {isNext && expectedArr && expectedArr !== 'Not available' && (
                              <div className="text-blue-700 font-bold mt-0.5">
                                <span className="text-[10px] text-blue-500 font-sans mr-1">Exp:</span>
                                <span>{expectedArr}</span>
                              </div>
                            )}

                            {/* Passed Station Actual Arrival */}
                            {isPassed && actArr && actArr !== 'Not available' && (
                              <div className="text-emerald-700 font-semibold mt-0.5">
                                <span className="text-[10px] text-emerald-500 font-sans mr-1">Act:</span>
                                <span>{actArr}</span>
                              </div>
                            )}

                            {/* Destination ETA */}
                            {isLast && destEta && destEta !== 'Not available' && (
                              <div className="text-emerald-700 font-bold mt-0.5">
                                <span className="text-[10px] text-emerald-500 font-sans mr-1">ETA:</span>
                                <span>{destEta}</span>
                              </div>
                            )}

                            {/* Fallback if no arrival information exists */}
                            {schedArr === 'Not available' &&
                              !expectedArr &&
                              !actArr &&
                              !destEta && (
                                <div className="text-slate-400 italic text-[11px] mt-0.5">
                                  {isFirst ? 'Origin Stop' : '--:--'}
                                </div>
                              )}
                          </div>

                          {/* Departure Timing */}
                          <div className="bg-white/80 p-2 rounded-lg border border-slate-200/80 min-w-[105px]">
                            <div className="text-[10px] font-sans font-semibold text-slate-400 uppercase flex items-center space-x-1">
                              <Clock className="w-3 h-3 text-slate-400" />
                              <span>Departure</span>
                            </div>

                            {/* Scheduled */}
                            {schedDep !== 'Not available' && (
                              <div className="text-slate-700 font-medium mt-0.5">
                                <span className="text-[10px] text-slate-400 font-sans mr-1">Sch:</span>
                                <span>{schedDep}</span>
                              </div>
                            )}

                            {/* Next Station Expected Departure */}
                            {isNext && expectedDep && expectedDep !== 'Not available' && (
                              <div className="text-blue-700 font-bold mt-0.5">
                                <span className="text-[10px] text-blue-500 font-sans mr-1">Exp:</span>
                                <span>{expectedDep}</span>
                              </div>
                            )}

                            {/* Passed Station Actual Departure */}
                            {isPassed && actDep && actDep !== 'Not available' && (
                              <div className="text-emerald-700 font-semibold mt-0.5">
                                <span className="text-[10px] text-emerald-500 font-sans mr-1">Act:</span>
                                <span>{actDep}</span>
                              </div>
                            )}

                            {/* Fallback if no departure timing exists */}
                            {schedDep === 'Not available' && !expectedDep && !actDep && (
                              <div className="text-slate-400 italic text-[11px] mt-0.5">
                                {isLast ? 'Terminus' : '--:--'}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteTimeline;
