import api from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';
import type { SongIngestRequest, SongIngestResponse } from '@/types';

/**
 * Ingest a song from YouTube.
 * Triggers the full pipeline: metadata, transcript, vectorization, Neo4j storage.
 */
export async function ingestSong(youtubeUrl: string): Promise<SongIngestResponse> {
  const payload: SongIngestRequest = { youtube_url: youtubeUrl };
  const { data } = await api.post<SongIngestResponse>(API_ENDPOINTS.SONG_INGEST, payload);
  return data;
}
