/**
 * Backend API endpoint constants.
 * Maps to FastAPI router prefixes defined in backend/app/api/*.py.
 */
export const API_ENDPOINTS = {
  HEALTH: '/health',
  SONG_INGEST: '/song/ingest',
  TRANSCRIPT: (songId: string) => `/transcript/${songId}` as const,
  TRANSLATE: '/translation/translate',
  TRANSLATIONS: (songId: string) => `/translation/song/${songId}` as const,
  RAG_ASK: '/rag/ask',
} as const;
