'use client';

import { useMutation } from '@tanstack/react-query';
import { askQuestion } from '@/services';
import { useSongStore } from '@/store/song-store';
import type { RAGAskRequest, RAGAskResponse } from '@/types';
import { generateSessionId } from '@/utils/generate-session-id';

/**
 * Mutation hook for asking a cultural interpretation question.
 * Appends user and assistant messages to the Zustand chat history.
 */
export function useRag() {
  const addMessage = useSongStore((s) => s.addMessage);
  const sessionId = useSongStore((s) => s.sessionId);
  const setSessionId = useSongStore((s) => s.setSessionId);

  return useMutation<RAGAskResponse, Error, { songId: string; question: string }>({
    mutationFn: async ({ songId, question }) => {
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        currentSessionId = generateSessionId();
        setSessionId(currentSessionId);
      }

      const request: RAGAskRequest = {
        song_id: songId,
        session_id: currentSessionId,
        question,
      };

      return askQuestion(request);
    },
    onMutate: ({ question }) => {
      addMessage({
        id: generateSessionId(),
        role: 'user',
        content: question,
        timestamp: new Date(),
      });
    },
    onSuccess: (data) => {
      addMessage({
        id: generateSessionId(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date(),
      });
    },
    onError: (error) => {
      addMessage({
        id: generateSessionId(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}`,
        timestamp: new Date(),
      });
    },
  });
}
