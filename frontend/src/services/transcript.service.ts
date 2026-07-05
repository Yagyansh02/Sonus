import api from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';
import type { TranscriptResponse } from '@/types';

/**
 * Retrieve the transcript for an ingested song.
 */
export async function getTranscript(songId: string): Promise<TranscriptResponse> {
  const { data } = await api.get<TranscriptResponse>(API_ENDPOINTS.TRANSCRIPT(songId));
  return data;
}
