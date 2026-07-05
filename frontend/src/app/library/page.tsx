'use client';

import { useRouter } from 'next/navigation';
import { Library as LibraryIcon } from 'lucide-react';
import { ROUTES } from '@/constants';
import { useSongStore } from '@/store/song-store';
import { PageHeader } from '@/components/layout/page-header';
import { Container } from '@/components/layout/container';
import { SongCard } from '@/components/cards/song-card';
import { EmptyState } from '@/components/shared/empty-state';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { FadeIn } from '@/components/animations/fade-in';
import Link from 'next/link';

/**
 * Library page — displays the currently ingested song.
 *
 * Note: The current backend does not have a "list all songs" endpoint,
 * so this page shows the last ingested song from Zustand.
 * When a list endpoint is added, this page can easily be extended
 * with a useQuery hook that fetches the full library.
 */
export default function LibraryPage() {
  const currentSong = useSongStore((s) => s.currentSong);
  const router = useRouter();

  return (
    <>
      <PageHeader
        title="Library"
        subtitle="Your analyzed songs collection. Every song you ingest lives here, ready for deeper exploration."
      />

      <Container className="pb-20">
        {currentSong ? (
          <FadeIn>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <SongCard
                song={currentSong}
                onClick={() => router.push(ROUTES.SONG(currentSong.song_id))}
              />
            </div>
          </FadeIn>
        ) : (
          <EmptyState
            icon={<LibraryIcon className="h-10 w-10" />}
            title="No Songs Yet"
            description="Your library is empty. Head to the Explore page to analyze your first song."
            action={
              <Link href={ROUTES.EXPLORE}>
                <PrimaryButton size="sm">Explore Songs</PrimaryButton>
              </Link>
            }
          />
        )}
      </Container>
    </>
  );
}
