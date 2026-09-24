import React from 'react';
import { Flag, Clock, Route } from 'lucide-react';
import { formatSafeText, formatTimeDisplay } from '../utils/formatters';

/**
 * Destination ETA Card: Displays destination station, ML-computed destination ETA,
 * and remaining distance. Displays 'Not available' when values are missing.
 */
export const DestinationCard = ({ train, prediction, route }) => {
  const destination = formatSafeText(train?.destination);
  const destinationEta = formatTimeDisplay(prediction?.destination_eta);
  const remainingDistance = route?.remaining_distance_km;

  const formattedDistance =
    remainingDistance !== null &&
    remainingDistance !== undefined &&
    !Number.isNaN(Number(remainingDistance))
      ? `${Math.round(Number(remainingDistance))} km`
      : 'Not available';

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 sm:p-6 flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 flex-wrap gap-2">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <Flag className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block truncate">
                Destination ETA
              </span>
              <span className="text-xs text-slate-400 block truncate">Terminating Station &amp; Arrival</span>
            </div>
          </div>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
            TERMINUS
          </span>
        </div>

        {/* Destination Station Name */}
        <div className="mt-4">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Destination Station
          </div>
          <h3
            className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight truncate mt-0.5"
            title={destination}
          >
            {destination}
          </h3>
          <p className="text-xs text-slate-500 mt-1">Final scheduled terminal of this train</p>
        </div>
      </div>

      {/* Metrics Grid: Destination ETA and Remaining Distance */}
      <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Destination ETA */}
        <div className="bg-emerald-50/60 p-3.5 rounded-lg border border-emerald-100">
          <div className="flex items-center space-x-1.5 text-xs text-emerald-800 font-bold uppercase tracking-wider mb-1">
            <Clock className="w-3.5 h-3.5 text-emerald-600" />
            <span>Destination ETA</span>
          </div>
          <div className="text-xl font-black font-mono text-emerald-700 mt-0.5">
            {destinationEta}
          </div>
          <div className="text-[10px] text-emerald-600/80 mt-0.5">Dynamic ML projected arrival</div>
        </div>

        {/* Remaining Distance */}
        <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200/80">
          <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">
            <Route className="w-3.5 h-3.5 text-slate-400" />
            <span>Remaining Distance</span>
          </div>
          <div className="text-xl font-black font-mono text-slate-900 mt-0.5">
            {formattedDistance}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Track distance to terminus</div>
        </div>
      </div>
    </div>
  );
};

export default DestinationCard;
