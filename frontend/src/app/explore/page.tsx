import type { Metadata } from 'next';
import { PageHeader } from '@/components/layout/page-header';
import { Container } from '@/components/layout/container';
import { IngestForm } from '@/components/sections/explore/ingest-form';
import { SongResult } from '@/components/sections/explore/song-result';

export const metadata: Metadata = {
  title: 'Explore',
  description: 'Ingest and analyze any song from YouTube. Paste a link and discover the cultural depth within.',
};

/**
 * Explore page — song ingestion and initial analysis.
 */
export default function ExplorePage() {
  return (
    <>
      <PageHeader
        title="Explore"
        subtitle="Paste a YouTube link to begin. We'll transcribe, classify, and prepare the song for deep cultural analysis."
      />
      <Container className="pb-20">
        <IngestForm />
        <SongResult />
      </Container>
    </>
  );
}
