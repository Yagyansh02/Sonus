import { create } from 'zustand';
import type { ChatMessage, SongIngestResponse } from '@/types';
import { generateSessionId } from '@/utils/generate-session-id';

/* ------------------------------------------------------------------ */
/*  State shape                                                        */
/* ------------------------------------------------------------------ */

interface SongState {
  /** Currently active song (set after ingestion or navigation). */
  currentSong: SongIngestResponse | null;

  /** RAG conversation session ID. */
  sessionId: string;

  /** RAG chat message history. */
  chatHistory: ChatMessage[];

  /* --- Actions --- */
  setSong: (song: SongIngestResponse) => void;
  clearSong: () => void;
  addMessage: (message: ChatMessage) => void;
  resetChat: () => void;
  setSessionId: (id: string) => void;
}

/* ------------------------------------------------------------------ */
/*  Store                                                              */
/* ------------------------------------------------------------------ */

export const useSongStore = create<SongState>((set) => ({
  currentSong: null,
  sessionId: '',
  chatHistory: [],

  setSong: (song) =>
    set({
      currentSong: song,
      sessionId: generateSessionId(),
      chatHistory: [],
    }),

  clearSong: () =>
    set({
      currentSong: null,
      sessionId: '',
      chatHistory: [],
    }),

  addMessage: (message) =>
    set((state) => ({
      chatHistory: [...state.chatHistory, message],
    })),

  resetChat: () =>
    set({
      sessionId: generateSessionId(),
      chatHistory: [],
    }),

  setSessionId: (id) => set({ sessionId: id }),
}));
