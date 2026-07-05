import api from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';
import type { HealthResponse } from '@/types';

/**
 * Check the backend system health.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>(API_ENDPOINTS.HEALTH);
  return data;
}
