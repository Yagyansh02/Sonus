'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { useIngestSong } from '@/hooks/use-ingest-song';
import { FadeIn } from '@/components/animations/fade-in';

const ingestSchema = z.object({
  youtubeUrl: z
    .string()
    .min(1, 'Please enter a YouTube URL')
    .url('Please enter a valid URL')
    .refine(
      (url) => {
        try {
          const parsed = new URL(url);
          return (
            parsed.hostname.includes('youtube.com') ||
            parsed.hostname.includes('youtu.be')
          );
        } catch {
          return false;
        }
      },
      { message: 'Must be a valid YouTube URL' },
    ),
});

type IngestFormData = z.infer<typeof ingestSchema>;

/**
 * YouTube URL input form with validation.
 * On submission, triggers the song ingestion pipeline.
 */
export function IngestForm() {
  const { mutate, isPending } = useIngestSong();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<IngestFormData>({
    resolver: zodResolver(ingestSchema),
    defaultValues: { youtubeUrl: '' },
  });

  function onSubmit(data: IngestFormData) {
    mutate(data.youtubeUrl);
  }

  return (
    <FadeIn>
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-col gap-4 sm:flex-row sm:items-end"
      >
        <div className="flex-1">
          <Input
            id="youtube-url"
            placeholder="https://www.youtube.com/watch?v=..."
            label="YouTube URL"
            error={errors.youtubeUrl?.message}
            {...register('youtubeUrl')}
          />
        </div>
        <PrimaryButton
          type="submit"
          isLoading={isPending}
          icon={<Search className="h-4 w-4" />}
          className="sm:mb-0"
        >
          {isPending ? 'Ingesting...' : 'Analyze Song'}
        </PrimaryButton>
      </form>
    </FadeIn>
  );
}
