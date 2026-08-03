import axios, { AxiosError, type AxiosInstance } from 'axios';
import type { ErrorResponse } from '@/types/api.types';

/**
 * Pre-configured Axios instance for communicating with the Sonus backend.
 *
 * - Base URL sourced from NEXT_PUBLIC_API_URL environment variable.
 * - JSON content type by default.
 * - 30-second timeout (ingestion can be slow).
 * - Response interceptor extracts API error messages.
 */
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api',
  timeout: 120_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* ------------------------------------------------------------------ */
/*  Response interceptor — normalise error shape                       */
/* ------------------------------------------------------------------ */
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      'An unexpected error occurred';

    const enrichedError = new Error(message);
    (enrichedError as Error & { statusCode?: number }).statusCode =
      error.response?.status;

    return Promise.reject(enrichedError);
  },
);

export default api;
