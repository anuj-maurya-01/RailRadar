import React from 'react';
import { Milestone, Clock, CalendarClock } from 'lucide-react';
import { formatSafeText, formatTimeDisplay } from '../utils/formatters';

/**
 * Next Station Card: Dedicated section displaying next station name, code,
 * scheduled arrival, expected arrival, scheduled departure, and expected departure.
 */
export const NextStationCard = ({ prediction }) => {
  const nextStationName = formatSafeText(prediction?.next_station);
  const stationCode = formatSafeText(prediction?.next_station_code);
  const scheduledArrival = formatTimeDisplay(prediction?.scheduled_arrival);
  const expectedArrival = formatTimeDisplay(prediction?.expected_arrival);
  const scheduledDeparture = formatTimeDisplay(prediction?.scheduled_departure);
  const expectedDeparture = formatTimeDisplay(prediction?.expected_departure);

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <Milestone className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block truncate">
                Next Station
              </span>
              <span className="text-xs text-slate-400 block truncate">Timetable &amp; Dynamic Arrival</span>
            </div>
          </div>
          {stationCode !== 'Not available' && (
            <span className="px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-800 text-xs font-mono font-bold border border-slate-200 shrink-0">
              {stationCode}
            </span>
          )}
        </div>

        {/* Station Name */}
        <div className="mt-4">
          <div className="flex items-baseline space-x-2 flex-wrap gap-y-1">
            <h3 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight break-words">
              {nextStationName}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-1">Upcoming scheduled station checkpoint</p>
        </div>
      </div>

      {/* Arrival & Departure Comparison Timings */}
      <div className="mt-6 pt-4 border-t border-slate-100 space-y-3">
        {/* Arrival Timings */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200/80">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold pb-2 border-b border-slate-200/60">
            <div className="flex items-center space-x-1.5">
              <CalendarClock className="w-3.5 h-3.5 text-blue-600" />
              <span className="uppercase tracking-wider">Arrival</span>
            </div>
            <span className="text-[11px] text-slate-400 font-normal">Timetable vs Expected</span>
          </div>

          <div className="mt-2.5 grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-[11px] font-medium text-slate-500">Scheduled Arrival</div>
              <div className="font-mono font-bold text-slate-800 text-base mt-0.5">
                {scheduledArrival}
              </div>
            </div>
            <div>
              <div className="text-[11px] font-bold text-blue-600">Expected Arrival</div>
              <div className="font-mono font-extrabold text-blue-700 text-base mt-0.5">
                {expectedArrival}
              </div>
            </div>
          </div>
        </div>

        {/* Departure Timings */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200/80">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold pb-2 border-b border-slate-200/60">
            <div className="flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span className="uppercase tracking-wider">Departure</span>
            </div>
            <span className="text-[11px] text-slate-400 font-normal">Timetable vs Expected</span>
          </div>

          <div className="mt-2.5 grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-[11px] font-medium text-slate-500">Scheduled Departure</div>
              <div className="font-mono font-bold text-slate-800 text-base mt-0.5">
                {scheduledDeparture}
              </div>
            </div>
            <div>
              <div className="text-[11px] font-bold text-blue-600">Expected Departure</div>
              <div className="font-mono font-extrabold text-blue-700 text-base mt-0.5">
                {expectedDeparture}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NextStationCard;
