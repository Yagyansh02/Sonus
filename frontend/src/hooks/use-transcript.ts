'use client';

import { useQuery } from '@tanstack/react-query';
import { getTranscript } from '@/services';
import type { TranscriptResponse } from '@/types';

/**
 * Query hook for fetching a song's transcript.
 * Only enabled when a valid songId is provided.
 */
export function useTranscript(songId: string | undefined) {
  return useQuery<TranscriptResponse, Error>({
    queryKey: ['transcript', songId],
    queryFn: () => getTranscript(songId!),
    enabled: !!songId,
    staleTime: Infinity,
    retry: 1,
  });
}
