import axios from 'axios';

// Update this if your backend runs on a different port
const API_BASE_URL = 'https://superb-exploration-production.up.railway.app/';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get token easily
export const getToken = () => localStorage.getItem('token');

// Automatically add Authorization header if available (Standard practice)
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;