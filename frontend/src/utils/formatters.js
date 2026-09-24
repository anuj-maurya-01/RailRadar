/**
 * Data formatting utilities for Railway ETA Dashboard.
 * Ensures null, undefined, or NaN values are never rendered to the user.
 */

/**
 * Safely format any text value, guaranteeing no 'null', 'undefined', or 'NaN' output.
 * @param {any} val
 * @param {string} [fallback='Not available']
 * @returns {string}
 */
export const formatSafeText = (val, fallback = 'Not available') => {
  if (val === null || val === undefined || val === '') {
    return fallback;
  }
  if (typeof val === 'number' && Number.isNaN(val)) {
    return fallback;
  }
  const str = String(val).trim();
  if (str === 'null' || str === 'undefined' || str === 'NaN') {
    return fallback;
  }
  return str;
};

/**
 * Format minutes delay into a professional signed badge string (e.g., "+32 min", "0 min (On Time)").
 * @param {number|string} val
 * @returns {string}
 */
export const formatDelayDisplay = (val) => {
  if (val === null || val === undefined || val === '') {
    return 'Not available';
  }
  const num = Number(val);
  if (Number.isNaN(num)) {
    return 'Not available';
  }
  if (num === 0) {
    return '0 min (On Time)';
  }
  if (num < 0) {
    return `${Math.round(num)} min (Early)`;
  }
  const rounded = Math.round(num * 10) / 10;
  // If whole number, format without .0
  const displayNum = Number.isInteger(rounded) ? rounded : rounded.toFixed(1);
  return `+${displayNum} min`;
};

/**
 * Format minutes delay for general text display.
 * @param {number|string} minutes
 * @returns {string}
 */
export const formatDelay = (minutes) => {
  if (minutes === null || minutes === undefined || minutes === '') return 'Not available';
  const num = Number(minutes);
  if (Number.isNaN(num)) return 'Not available';
  if (num <= 0) return '0 min (On Time)';
  if (num < 60) return `${Math.round(num)} min delay`;
  const hrs = Math.floor(num / 60);
  const mins = Math.round(num % 60);
  return mins > 0 ? `${hrs}h ${mins}m delay` : `${hrs}h delay`;
};

/**
 * Format train speed in km/h.
 * @param {number|string} speed
 * @returns {string}
 */
export const formatSpeed = (speed) => {
  if (speed === null || speed === undefined || speed === '') {
    return 'Not available';
  }
  const num = Number(speed);
  if (Number.isNaN(num)) {
    return 'Not available';
  }
  return `${Math.round(num)} km/h`;
};

/**
 * Format time string ("HH:MM") safely.
 * @param {string} timeStr
 * @returns {string}
 */
export const formatTimeDisplay = (timeStr) => {
  if (!timeStr) return 'Not available';
  const str = String(timeStr).trim();
  if (str === 'null' || str === 'undefined' || str === '' || str === 'NaN') {
    return 'Not available';
  }
  // If ISO 8601 string containing 'T', extract HH:MM
  if (str.includes('T')) {
    const timePart = str.split('T')[1];
    if (timePart) {
      const match = timePart.match(/^(\d{1,2}:\d{2})/);
      if (match) return match[1];
    }
  }
  // If standard HH:MM:SS, extract HH:MM
  const match = str.match(/^(\d{1,2}:\d{2})(?::\d{2})?/);
  if (match && match[1]) {
    return match[1];
  }
  return str;
};

/**
 * Safely format station name and station code.
 * @param {string} name
 * @param {string} code
 * @returns {string}
 */
export const formatStation = (name, code) => {
  const cleanName = name && String(name).trim() !== 'null' && String(name).trim() !== 'undefined'
    ? String(name).trim()
    : null;
  const cleanCode = code && String(code).trim() !== 'null' && String(code).trim() !== 'undefined'
    ? String(code).trim()
    : null;

  if (cleanName && cleanCode) {
    return `${cleanName} (${cleanCode})`;
  }
  if (cleanName) {
    return cleanName;
  }
  if (cleanCode) {
    return cleanCode;
  }
  return 'Not available';
};

export default {
  formatSafeText,
  formatDelayDisplay,
  formatDelay,
  formatSpeed,
  formatTimeDisplay,
  formatStation,
};
