'use client';

import { useRouter } from 'next/navigation';
import { ROUTES } from '@/constants';
import { useSongStore } from '@/store/song-store';
import { SongCard } from '@/components/cards/song-card';
import { QuickActions } from './quick-actions';
import { FadeIn } from '@/components/animations/fade-in';

/**
 * Displays the ingested song result with action buttons.
 * Renders only when a song exists in the store.
 */
export function SongResult() {
  const currentSong = useSongStore((s) => s.currentSong);
  const router = useRouter();

  if (!currentSong) return null;

  return (
    <FadeIn className="mt-12">
      <div className="grid gap-8 lg:grid-cols-[1fr_1.2fr]">
        <SongCard
          song={currentSong}
          onClick={() => router.push(ROUTES.SONG(currentSong.song_id))}
        />
        <QuickActions songId={currentSong.song_id} />
      </div>
    </FadeIn>
  );
}
