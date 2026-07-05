import api from '@/lib/api';
import { API_ENDPOINTS } from '@/constants';
import type { TranslateRequest, TranslationResponse, TranslationListResponse } from '@/types';

/**
 * Translate a song's lyrics into the specified target language.
 */
export async function translateSong(
  request: TranslateRequest,
): Promise<TranslationResponse> {
  const { data } = await api.post<TranslationResponse>(API_ENDPOINTS.TRANSLATE, request);
  return data;
}

/**
 * List all existing translations for a song.
 */
export async function getTranslations(songId: string): Promise<TranslationListResponse> {
  const { data } = await api.get<TranslationListResponse>(API_ENDPOINTS.TRANSLATIONS(songId));
  return data;
}
