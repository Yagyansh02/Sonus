'use client';

import { Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { useTranscript } from '@/hooks/use-transcript';
import { IconButton } from '@/components/buttons/icon-button';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { ErrorState } from '@/components/shared/error-state';
import { EmptyState } from '@/components/shared/empty-state';
import { FileText } from 'lucide-react';
import { FadeIn } from '@/components/animations/fade-in';

interface TranscriptTabProps {
  songId: string;
}

/**
 * Transcript display tab with copy-to-clipboard functionality.
 */
export function TranscriptTab({ songId }: TranscriptTabProps) {
  const { data, isLoading, isError, error, refetch } = useTranscript(songId);
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!data?.content) return;
    await navigator.clipboard.writeText(data.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <LoadingSpinner size="lg" label="Loading transcript" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        message={error?.message || 'Failed to load transcript'}
        onRetry={() => refetch()}
      />
    );
  }

  if (!data?.content) {
    return (
      <EmptyState
        icon={<FileText className="h-10 w-10" />}
        title="No Transcript"
        description="No transcript is available for this song yet."
      />
    );
  }

  return (
    <FadeIn>
      <div
        className="relative rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] p-8"
        role="tabpanel"
        id="tabpanel-transcript"
      >
        {/* Copy button */}
        <div className="absolute right-4 top-4">
          <IconButton
            icon={
              copied ? (
                <Check className="h-4 w-4 text-green-400" />
              ) : (
                <Copy className="h-4 w-4" />
              )
            }
            label={copied ? 'Copied!' : 'Copy transcript'}
            onClick={handleCopy}
          />
        </div>

        {/* Source badge */}
        <div className="mb-6">
          <span className="text-xs font-medium tracking-wider text-[#8D8D8D] uppercase">
            Source: {data.source}
          </span>
        </div>

        {/* Lyrics */}
        <div className="whitespace-pre-wrap text-[#CFC8BE] leading-relaxed font-body text-base">
          {data.content}
        </div>
      </div>
    </FadeIn>
  );
}
