'use client';

import { useSearchParams } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';
import { FileText, Languages, MessageCircle } from 'lucide-react';
import { useSongStore } from '@/store/song-store';
import { Container } from '@/components/layout/container';
import { Tabs } from '@/components/ui/tabs';
import { SongHeader } from '@/components/sections/song/song-header';
import { TranscriptTab } from '@/components/sections/song/transcript-tab';
import { TranslationTab } from '@/components/sections/song/translation-tab';
import { InterpretationTab } from '@/components/sections/song/interpretation-tab';
import { EmptyState } from '@/components/shared/empty-state';
import { Music } from 'lucide-react';
import Link from 'next/link';
import { ROUTES } from '@/constants';
import { PrimaryButton } from '@/components/buttons/primary-button';

const TABS = [
  { id: 'transcript', label: 'Transcript', icon: <FileText className="h-4 w-4" /> },
  { id: 'translation', label: 'Translate', icon: <Languages className="h-4 w-4" /> },
  { id: 'interpretation', label: 'Interpret', icon: <MessageCircle className="h-4 w-4" /> },
] as const;

/**
 * Inner component that reads search params (must be inside Suspense).
 */
function SongDetailContent({ songId }: { songId: string }) {
  const searchParams = useSearchParams();
  const currentSong = useSongStore((s) => s.currentSong);
  const [activeTab, setActiveTab] = useState('transcript');

  /** Sync tab from URL query param on mount. */
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && TABS.some((t) => t.id === tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  if (!currentSong || currentSong.song_id !== songId) {
    return (
      <div className="pt-32 pb-20">
        <Container>
          <EmptyState
            icon={<Music className="h-10 w-10" />}
            title="Song Not Found"
            description="This song hasn't been ingested yet. Go to the Explore page to analyze a song first."
            action={
              <Link href={ROUTES.EXPLORE}>
                <PrimaryButton size="sm">Go to Explore</PrimaryButton>
              </Link>
            }
          />
        </Container>
      </div>
    );
  }

  return (
    <>
      <SongHeader song={currentSong} />

      <Container className="pb-20">
        {/* Tab navigation */}
        <div className="mb-8 flex justify-center">
          <Tabs
            tabs={TABS.map((t) => ({ ...t }))}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {/* Tab content */}
        {activeTab === 'transcript' && (
          <TranscriptTab songId={currentSong.song_id} />
        )}
        {activeTab === 'translation' && (
          <TranslationTab songId={currentSong.song_id} />
        )}
        {activeTab === 'interpretation' && (
          <InterpretationTab songId={currentSong.song_id} />
        )}
      </Container>
    </>
  );
}

/**
 * Song detail page — full song view with tabs for Transcript, Translate, and Interpret.
 * Uses dynamic route param [id].
 */
export default function SongDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [songId, setSongId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setSongId(p.id));
  }, [params]);

  if (!songId) return null;

  return (
    <Suspense>
      <SongDetailContent songId={songId} />
    </Suspense>
  );
}
