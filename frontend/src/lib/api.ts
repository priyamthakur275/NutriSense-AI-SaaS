import axios from "axios";
import { useAuthStore } from "@/store/authStore";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const wasAuthenticated = useAuthStore.getState().isAuthenticated;
      useAuthStore.getState().logout();

      if (wasAuthenticated && typeof window !== "undefined") {
        window.location.href = "/session-expired";
      }
    }
    return Promise.reject(error);
  }
);
