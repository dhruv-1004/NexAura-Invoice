import axios from 'axios';

// Dynamically use the current host so network sharing works (e.g. 192.168.x.x)
const localUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8000' 
  : `http://${window.location.hostname}:8000`;

const API_URL = import.meta.env.VITE_API_URL || localUrl;

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
