import React, { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Navigation, AlertCircle, Loader2 } from 'lucide-react';
import { formatSafeText, formatDelayDisplay, formatSpeed, formatTimeDisplay } from '../utils/formatters';

/**
 * Custom modern DivIcons for Leaflet markers.
 * Avoids broken default Leaflet image asset URLs in Vite production builds.
 */
const trainIcon = L.divIcon({
  className: 'custom-train-marker',
  html: `
    <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
      <span style="position: absolute; width: 36px; height: 36px; border-radius: 9999px; background-color: rgba(59, 130, 246, 0.4); animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></span>
      <div style="position: relative; width: 30px; height: 30px; border-radius: 9999px; background-color: #2563eb; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2); border: 2px solid #ffffff; font-size: 14px;">
        🚆
      </div>
    </div>
  `,
  iconSize: [36, 36],
  iconAnchor: [18, 18],
  popupAnchor: [0, -18],
});

const currentStationIcon = L.divIcon({
  className: 'custom-station-current',
  html: `
    <div style="display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
      <div style="width: 24px; height: 24px; border-radius: 9999px; background-color: #059669; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 2px solid #ffffff; font-size: 11px;">
        📍
      </div>
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

const nextStationIcon = L.divIcon({
  className: 'custom-station-next',
  html: `
    <div style="display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
      <div style="width: 24px; height: 24px; border-radius: 9999px; background-color: #d97706; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 2px solid #ffffff; font-size: 11px;">
        🎯
      </div>
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

const destinationIcon = L.divIcon({
  className: 'custom-station-dest',
  html: `
    <div style="display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
      <div style="width: 24px; height: 24px; border-radius: 9999px; background-color: #dc2626; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); border: 2px solid #ffffff; font-size: 11px;">
        🏁
      </div>
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

const waypointIcon = L.divIcon({
  className: 'custom-station-waypoint',
  html: `
    <div style="width: 10px; height: 10px; border-radius: 9999px; background-color: #64748b; border: 2px solid #ffffff; box-shadow: 0 1px 2px rgba(0,0,0,0.3);"></div>
  `,
  iconSize: [10, 10],
  iconAnchor: [5, 5],
  popupAnchor: [0, -6],
});

/**
 * Safely parse a coordinate pair [latitude, longitude].
 */
const extractCoords = (obj) => {
  if (!obj) return null;
  const lat = Number(obj.latitude ?? obj.lat);
  const lng = Number(obj.longitude ?? obj.lng ?? obj.lon);
  if (!Number.isNaN(lat) && !Number.isNaN(lng) && lat !== 0 && lng !== 0) {
    if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
      return [lat, lng];
    }
  }

  // Check coordinates array (e.g. GeoJSON [lng, lat])
  if (Array.isArray(obj.coordinates) && obj.coordinates.length >= 2) {
    const c0 = Number(obj.coordinates[0]);
    const c1 = Number(obj.coordinates[1]);
    if (!Number.isNaN(c0) && !Number.isNaN(c1)) {
      if (c1 >= -90 && c1 <= 90 && c0 >= -180 && c0 <= 180) {
        return [c1, c0];
      }
      if (c0 >= -90 && c0 <= 90 && c1 >= -180 && c1 <= 180) {
        return [c0, c1];
      }
    }
  }
  return null;
};

/**
 * Pure function to resolve geographic and telemetry points from trainData.
 */
const resolveMapData = (trainData) => {
  if (!trainData) {
    return {
      stationsWithCoords: [],
      currentCoords: null,
      nextCoords: null,
      destCoords: null,
      trainPosition: null,
      isGps: false,
      progressPercent: null,
      routePolyline: [],
      allPoints: [],
    };
  }

  const liveStatus = trainData.live_status || {};
  const prediction = trainData.prediction || {};
  const route = trainData.route || {};
  const train = trainData.train || {};

  // 1. Process Route Stations with valid coordinates
  const rawStations = Array.isArray(route.stations) ? route.stations : [];
  const stationsWithCoords = rawStations
    .map((stn, idx) => {
      const coords = extractCoords(stn);
      if (!coords) return null;
      return {
        ...stn,
        code: stn.stationCode || stn.station_code || stn.code,
        name: stn.stationName || stn.station_name || stn.name,
        sequence: stn.sequence ?? idx + 1,
        coords,
      };
    })
    .filter(Boolean);

  // 2. Identify Key Station Coordinates
  const currentStnCode = (liveStatus.current_station_code || '').toUpperCase();
  const nextStnCode = (prediction.next_station_code || '').toUpperCase();
  const destCode = (train.destination || '').toUpperCase();
  const currentSeq = liveStatus.current_sequence;
  const currentName = (liveStatus.current_station_name || '').toUpperCase();

  const currentStnObj = stationsWithCoords.find(
    (s) =>
      (currentSeq !== null && currentSeq !== undefined && Number(s.sequence) === Number(currentSeq)) ||
      (s.code && currentStnCode && s.code.toUpperCase() === currentStnCode) ||
      (s.name && currentName && s.name.toUpperCase().includes(currentName))
  );
  const nextStnObj = stationsWithCoords.find(
    (s) =>
      (s.code && nextStnCode && s.code.toUpperCase() === nextStnCode) ||
      (s.name && prediction.next_station && s.name.toUpperCase().includes(prediction.next_station.toUpperCase()))
  );
  const destStnObj = stationsWithCoords.find(
    (s) =>
      (s.code && s.code.toUpperCase() === destCode) ||
      (s.name && s.name.toUpperCase().includes(destCode))
  );

  const currentCoords = currentStnObj ? currentStnObj.coords : extractCoords(liveStatus);
  const nextCoords = nextStnObj ? nextStnObj.coords : extractCoords(prediction);
  const destCoords = destStnObj ? destStnObj.coords : null;

  // 3. Determine Train Marker Position
  let trainPosition = null;
  let isGps = false;
  let progressPercent = null;

  const directGps = extractCoords(liveStatus);
  if (directGps) {
    trainPosition = directGps;
    isGps = true;
  } else {
    const segProg = liveStatus.segment_progress;
    if (currentCoords && nextCoords && segProg !== null && segProg !== undefined) {
      const numProg = Number(segProg);
      if (!Number.isNaN(numProg)) {
        const progress = Math.max(0.0, Math.min(1.0, numProg));
        const estLat = currentCoords[0] + progress * (nextCoords[0] - currentCoords[0]);
        const estLng = currentCoords[1] + progress * (nextCoords[1] - currentCoords[1]);
        trainPosition = [estLat, estLng];
        isGps = false;
        progressPercent = Math.round(progress * 100);
      }
    }
  }

  // Fallback to guarantee train position is always visible
  if (!trainPosition) {
    if (currentCoords) {
      trainPosition = currentCoords;
      isGps = false;
    } else if (nextCoords) {
      trainPosition = nextCoords;
      isGps = false;
    } else if (stationsWithCoords.length > 0) {
      trainPosition = stationsWithCoords[0].coords;
      isGps = false;
    }
  }

  // 4. Resolve Route Polyline Coordinates
  let routePolyline = [];
  if (Array.isArray(route.coordinates) && route.coordinates.length >= 2) {
    const parsed = route.coordinates.map(extractCoords).filter(Boolean);
    if (parsed.length >= 2) {
      routePolyline = parsed;
    }
  }

  if (routePolyline.length === 0 && stationsWithCoords.length >= 2) {
    routePolyline = stationsWithCoords.map((s) => s.coords);
  } else if (routePolyline.length === 0 && currentCoords && nextCoords) {
    routePolyline = [currentCoords, nextCoords];
  }

  // 5. Aggregate all active geographic points
  const allPoints = [];
  if (trainPosition) allPoints.push(trainPosition);
  if (currentCoords) allPoints.push(currentCoords);
  if (nextCoords) allPoints.push(nextCoords);
  if (destCoords) allPoints.push(destCoords);
  stationsWithCoords.forEach((s) => allPoints.push(s.coords));
  routePolyline.forEach((p) => allPoints.push(p));

  return {
    stationsWithCoords,
    currentCoords,
    nextCoords,
    destCoords,
    currentStnCode,
    nextStnCode,
    destCode,
    trainPosition,
    isGps,
    progressPercent,
    routePolyline,
    allPoints,
  };
};

/**
 * Automatically fits Leaflet map bounds around all active route points.
 */
function MapBoundsFitter({ bounds }) {
  const map = useMap();

  useEffect(() => {
    // Recalculate container dimensions in case of flex/grid reflow
    map.invalidateSize();

    if (bounds && bounds.isValid()) {
      map.fitBounds(bounds, {
        padding: [45, 45],
        maxZoom: 13,
        animate: true,
      });
    }
  }, [map, bounds]);

  return null;
}

/**
 * TrainMap Component: Displays OpenStreetMap with actual railway route,
 * station markers, and train position (GPS or segment progress estimated).
 */
export const TrainMap = ({
  trainData,
  activeTrains = [],
  onSelectTrain = () => {},
  loading = false,
}) => {
  // Always call useMemo unconditionally at the top level
  const mapData = useMemo(() => resolveMapData(trainData), [trainData]);

  // Loading state placeholder
  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 p-8 shadow-xs flex flex-col items-center justify-center min-h-[380px] text-center">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
        <div className="text-sm font-bold text-slate-800 dark:text-slate-200">Loading railway route geometry...</div>
        <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Fetching live station checkpoints and tracking coordinates</div>
      </div>
    );
  }

  // If no specific train is selected, display live national network map
  if (!trainData) {
    const validTrainPoints = (activeTrains || [])
      .filter((t) => t.latitude && t.longitude)
      .map((t) => [Number(t.latitude), Number(t.longitude)]);

    const overviewCenter = [21.5, 78.9];
    const overviewBounds = validTrainPoints.length > 0 ? L.latLngBounds(validTrainPoints) : null;

    return (
      <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs overflow-hidden h-full flex flex-col">
        {/* Map Header with Legend */}
        <div className="px-4 sm:px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/70 dark:bg-slate-800/50">
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
              <Navigation className="w-3.5 h-3.5" />
            </div>
            <div>
              <h3 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                Live National Railway Map
              </h3>
              <p className="text-[10px] text-slate-500 dark:text-slate-400">
                Active tracked express trains across Indian Railways
              </p>
            </div>
          </div>
          <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400">
            {(activeTrains || []).length} Trains Active
          </span>
        </div>

        {/* Leaflet Canvas */}
        <div className="h-[380px] sm:h-[440px] w-full relative z-0">
          <MapContainer
            center={overviewCenter}
            zoom={5}
            minZoom={4}
            maxZoom={14}
            scrollWheelZoom={true}
            className="h-full w-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {overviewBounds && <MapBoundsFitter bounds={overviewBounds} />}

            {(activeTrains || [])
              .filter((t) => t.latitude && t.longitude)
              .map((t) => (
                <Marker
                  key={t.train_number}
                  position={[Number(t.latitude), Number(t.longitude)]}
                  icon={trainIcon}
                  eventHandlers={{
                    click: () => onSelectTrain(t.train_number, t),
                  }}
                >
                  <Popup>
                    <div className="text-xs p-1">
                      <div className="font-bold text-slate-900">
                        {t.train_number} - {t.train_name}
                      </div>
                      <div className="text-slate-600 text-[11px] mt-0.5">
                        {t.source} → {t.destination}
                      </div>
                      <div className="text-slate-500 text-[10px] mt-0.5">
                        Current: <strong>{t.current_station_name}</strong>
                      </div>
                      <div className="mt-1 font-semibold text-[10px] text-blue-600">
                        Click to track this train →
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
          </MapContainer>
        </div>
      </div>
    );
  }

  const {
    stationsWithCoords,
    currentCoords,
    nextCoords,
    destCoords,
    currentStnCode,
    nextStnCode,
    destCode,
    trainPosition,
    isGps,
    progressPercent,
    routePolyline,
    allPoints,
  } = mapData;

  const liveStatus = trainData.live_status || {};
  const prediction = trainData.prediction || {};
  const train = trainData.train || {};

  // Requirement 15: No Coordinates Case
  if (allPoints.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-100 mb-4">
          <Navigation className="w-5 h-5 text-slate-400" />
          <h3 className="text-base font-bold text-slate-900">Live Railway Route Map</h3>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 sm:p-8 text-center max-w-lg mx-auto">
          <div className="w-12 h-12 rounded-full bg-slate-200/80 flex items-center justify-center text-slate-500 mx-auto mb-3">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h4 className="text-sm sm:text-base font-bold text-slate-800">
            Live map location is not available for this train.
          </h4>
          <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
            Geographic coordinates are not exposed by the railway telemetry feed for this service.
            The dashboard status and arrival predictions remain active above.
          </p>
        </div>
      </div>
    );
  }

  // Calculate Leaflet bounds
  const bounds = L.latLngBounds(allPoints);
  const initialCenter = trainPosition || allPoints[0] || [20.5937, 78.9629];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/90 dark:border-slate-800 shadow-xs overflow-hidden">
      {/* Map Header with Legend */}
      <div className="px-4 sm:px-5 py-3.5 border-b border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 bg-slate-50/70 dark:bg-slate-800/50">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <Navigation className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
              Live Railway Route Map
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {isGps
                ? 'GPS Tracking Active'
                : trainPosition
                ? `Interpolated Position (Segment Progress: ${progressPercent}%)`
                : 'Station Route Corridor'}
            </p>
          </div>
        </div>

        {/* Legend Pills */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-medium text-slate-600">
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            <span>🚆</span>
            <span>Train</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span>📍</span>
            <span>Current Stop</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
            <span>🎯</span>
            <span>Next Stop</span>
          </div>
          <div className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
            <span>🏁</span>
            <span>Terminus</span>
          </div>
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div className="h-[380px] sm:h-[480px] lg:h-[540px] w-full relative z-0">
        <MapContainer
          center={initialCenter}
          zoom={8}
          scrollWheelZoom={false}
          className="h-full w-full"
        >
          {/* OpenStreetMap Tile Layer with Required Attribution */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />

          {/* Dynamic Auto-Fit Bounds */}
          <MapBoundsFitter bounds={bounds} />

          {/* Railway Route Polyline */}
          {routePolyline.length >= 2 && (
            <Polyline
              positions={routePolyline}
              pathOptions={{
                color: '#2563eb',
                weight: 4,
                opacity: 0.85,
                lineCap: 'round',
                lineJoin: 'round',
              }}
            />
          )}

          {/* Intermediate Route Station Waypoints */}
          {stationsWithCoords.map((stn) => {
            const isCurr = stn.code && stn.code.toUpperCase() === currentStnCode;
            const isNext = stn.code && stn.code.toUpperCase() === nextStnCode;
            const isDest = stn.code && stn.code.toUpperCase() === destCode;

            // Render primary markers separately
            if (isCurr || isNext || isDest) return null;

            return (
              <Marker key={`waypoint-${stn.code || stn.sequence}`} position={stn.coords} icon={waypointIcon}>
                <Popup>
                  <div className="text-xs space-y-1">
                    <div className="font-bold text-slate-800">{formatSafeText(stn.name)}</div>
                    <div className="font-mono text-slate-500">Station Code: {formatSafeText(stn.code)}</div>
                    {stn.distance !== undefined && stn.distance !== null && (
                      <div className="text-slate-500">Route Distance: {stn.distance} km</div>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Current Station Marker */}
          {currentCoords && (
            <Marker position={currentCoords} icon={currentStationIcon}>
              <Popup>
                <div className="text-xs space-y-1 p-0.5">
                  <div className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider">
                    Current Station
                  </div>
                  <div className="font-bold text-slate-900 text-sm">
                    {formatSafeText(liveStatus.current_station_name)}
                  </div>
                  <div className="font-mono text-slate-500">
                    Code: {formatSafeText(liveStatus.current_station_code)}
                  </div>
                  <div className="pt-1 border-t border-slate-100 text-slate-700">
                    <span className="font-medium">LIVE DELAY:</span>{' '}
                    <span className="font-mono font-bold text-amber-600">
                      {formatDelayDisplay(liveStatus.current_delay_minutes)}
                    </span>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Next Station Marker */}
          {nextCoords && (
            <Marker position={nextCoords} icon={nextStationIcon}>
              <Popup>
                <div className="text-xs space-y-1 p-0.5">
                  <div className="text-[10px] font-bold text-amber-600 uppercase tracking-wider">
                    Next Station
                  </div>
                  <div className="font-bold text-slate-900 text-sm">
                    {formatSafeText(prediction.next_station)}
                  </div>
                  <div className="font-mono text-slate-500">
                    Code: {formatSafeText(prediction.next_station_code)}
                  </div>
                  <div className="pt-1 border-t border-slate-100 space-y-0.5 text-slate-700">
                    <div>
                      <span className="text-slate-500">Scheduled:</span>{' '}
                      <span className="font-mono font-bold">{formatTimeDisplay(prediction.scheduled_arrival)}</span>
                    </div>
                    <div>
                      <span className="text-blue-600 font-medium">Expected (ML):</span>{' '}
                      <span className="font-mono font-bold text-blue-700">
                        {formatTimeDisplay(prediction.expected_arrival)}
                      </span>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Destination Marker */}
          {destCoords && (
            <Marker position={destCoords} icon={destinationIcon}>
              <Popup>
                <div className="text-xs space-y-1 p-0.5">
                  <div className="text-[10px] font-bold text-rose-600 uppercase tracking-wider">
                    Terminus Destination
                  </div>
                  <div className="font-bold text-slate-900 text-sm">
                    {formatSafeText(train.destination)}
                  </div>
                  <div className="pt-1 border-t border-slate-100 text-slate-700">
                    <span className="font-medium">Destination ETA:</span>{' '}
                    <span className="font-mono font-bold text-emerald-700">
                      {formatTimeDisplay(prediction.destination_eta)}
                    </span>
                  </div>
                </div>
              </Popup>
            </Marker>
          )}

          {/* Train Position Marker */}
          {trainPosition && (
            <Marker position={trainPosition} icon={trainIcon} zIndexOffset={1000}>
              <Popup>
                <div className="text-xs space-y-1.5 p-1 min-w-[200px]">
                  <div className="flex items-center justify-between pb-1 border-b border-slate-100">
                    <span className="font-bold text-slate-900">
                      🚆 Train #{formatSafeText(train.train_number)}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 font-medium">
                      {isGps ? 'GPS' : 'Estimated'}
                    </span>
                  </div>

                  <div className="font-medium text-slate-800">
                    {formatSafeText(train.train_name)}
                  </div>

                  <div className="grid grid-cols-2 gap-1.5 pt-1 border-t border-slate-100 text-[11px]">
                    <div>
                      <div className="text-slate-400">Current Stop</div>
                      <div className="font-semibold text-slate-700 truncate">
                        {formatSafeText(liveStatus.current_station_name)}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400">Next Stop</div>
                      <div className="font-semibold text-slate-700 truncate">
                        {formatSafeText(prediction.next_station)}
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px]">
                    <div>
                      <div className="text-slate-400">LIVE DELAY</div>
                      <div className="font-mono font-bold text-amber-600">
                        {formatDelayDisplay(liveStatus.current_delay_minutes)}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-400">ML Forecast</div>
                      <div className="font-mono font-bold text-indigo-600">
                        {formatDelayDisplay(prediction.predicted_delay_minutes)}
                      </div>
                    </div>
                  </div>

                  <div className="pt-1 border-t border-slate-100 flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Speed:</span>
                    <span className="font-mono font-bold text-slate-800">
                      {formatSpeed(liveStatus.speed_kmh)}
                    </span>
                  </div>

                  {!isGps && progressPercent !== null && (
                    <div className="text-[10px] text-slate-400 italic pt-0.5">
                      Estimated ~{progressPercent}% between stations
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    </div>
  );
};

export default TrainMap;
