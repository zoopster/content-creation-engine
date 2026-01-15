/**
 * API client configuration.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 'An error occurred';
      console.error(`[API Error] ${error.response.status}: ${message}`);
      throw new Error(message);
    } else if (error.request) {
      // Request made but no response
      throw new Error('Unable to connect to server');
    } else {
      throw error;
    }
  }
);
