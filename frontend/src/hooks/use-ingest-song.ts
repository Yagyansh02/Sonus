'use client';

import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ingestSong } from '@/services';
import { useSongStore } from '@/store/song-store';
import type { SongIngestResponse } from '@/types';

/**
 * Mutation hook for ingesting a song from YouTube.
 * On success, stores the song in Zustand and shows a toast.
 */
export function useIngestSong() {
  const setSong = useSongStore((s) => s.setSong);

  return useMutation<SongIngestResponse, Error, string>({
    mutationFn: ingestSong,
    onSuccess: (data) => {
      setSong(data);
      toast.success(`"${data.title}" by ${data.artist} ingested successfully`);
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to ingest song');
    },
  });
}
