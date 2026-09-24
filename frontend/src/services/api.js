import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Pre-configured Axios instance for communicating with the FastAPI backend.
 * Uses VITE_API_BASE_URL without hardcoding backend URLs in React components.
 * Never connects directly to external railway APIs or exposes backend secrets.
 */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

/**
 * Fetch real-time live tracking and ML ETA predictions for a specific train.
 * Calls: GET ${VITE_API_BASE_URL}/api/train/{trainNumber}
 *
 * @param {string|number} trainNumber 5-digit Indian Railways train number (e.g. 11013)
 * @returns {Promise<object>} Frontend-ready train tracking & prediction object
 */
export const getTrain = async (trainNumber) => {
  const cleanNumber = String(trainNumber || '').trim();
  const response = await apiClient.get(`/api/train/${encodeURIComponent(cleanNumber)}`);
  return response.data;
};

/**
 * Check backend service availability.
 * @returns {Promise<object>} Health check status
 */
export const getHealth = async () => {
  const response = await apiClient.get('/api/health');
  return response.data;
};

/**
 * Retrieve status of the periodic data collection scheduler.
 * @returns {Promise<object>} Collection scheduler status
 */
export const getCollectionStatus = async () => {
  const response = await apiClient.get('/api/collection/status');
  return response.data;
};

export default {
  apiClient,
  getTrain,
  getHealth,
  getCollectionStatus,
};
