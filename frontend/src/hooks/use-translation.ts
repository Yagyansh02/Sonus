'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { translateSong, getTranslations } from '@/services';
import type { TranslateRequest, TranslationResponse, TranslationListResponse } from '@/types';

/**
 * Mutation hook for translating a song's lyrics.
 * Invalidates the translations list cache on success.
 */
export function useTranslateSong() {
  const queryClient = useQueryClient();

  return useMutation<TranslationResponse, Error, TranslateRequest>({
    mutationFn: translateSong,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['translations', data.song_id] });
      toast.success(`Translated to ${data.target_language}`);
    },
    onError: (error) => {
      toast.error(error.message || 'Translation failed');
    },
  });
}

/**
 * Query hook for listing all translations of a song.
 */
export function useTranslations(songId: string | undefined) {
  return useQuery<TranslationListResponse, Error>({
    queryKey: ['translations', songId],
    queryFn: () => getTranslations(songId!),
    enabled: !!songId,
    staleTime: 30_000,
  });
}
