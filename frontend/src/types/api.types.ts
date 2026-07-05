/* ================================================================== */
/*  Backend API type definitions                                       */
/*  Mirror of: backend/app/schemas/*                                   */
/* ================================================================== */

/* ----------------------- Error ------------------------------------ */

export interface ErrorResponse {
  detail: string;
  error_code: string;
}

/* ----------------------- Health ----------------------------------- */

export interface ServiceStatus {
  neo4j: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: ServiceStatus;
}

/* ----------------------- Song ------------------------------------- */

export interface SongIngestRequest {
  youtube_url: string;
}

export interface SongIngestResponse {
  song_id: string;
  title: string;
  artist: string;
  thumbnail: string;
  language: string;
  genres: string[];
  cultural_themes: string[];
  mood: string;
  era: string;
  message?: string;
}

/* ----------------------- Transcript ------------------------------- */

export interface TranscriptResponse {
  transcript_id: string;
  song_id: string;
  content: string;
  source: string;
}

/* ----------------------- Translation ------------------------------ */

export interface TranslateRequest {
  song_id?: string;
  youtube_url?: string;
  target_language: string;
}

export interface TranslationResponse {
  translation_id: string;
  song_id: string;
  target_language: string;
  translated_lyrics: string;
  translation_notes: string;
  confidence_score: number;
}

export interface TranslationListResponse {
  song_id: string;
  translations: TranslationResponse[];
  count: number;
}

/* ----------------------- RAG -------------------------------------- */

export interface RAGAskRequest {
  song_id: string;
  session_id: string;
  question: string;
}

export interface RAGAskResponse {
  answer: string;
  sources: string[];
  session_id: string;
  song_id: string;
}

/* ----------------------- Chat (Frontend-only) --------------------- */

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
}
