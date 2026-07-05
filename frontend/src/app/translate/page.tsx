'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Languages, Search, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { LANGUAGES, ROUTES } from '@/constants';
import { PageHeader } from '@/components/layout/page-header';
import { Container } from '@/components/layout/container';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { SecondaryButton } from '@/components/buttons/secondary-button';
import { Badge } from '@/components/ui/badge';
import { FadeIn } from '@/components/animations/fade-in';
import { useIngestSong } from '@/hooks/use-ingest-song';
import { useTranslateSong } from '@/hooks/use-translation';
import { useSongStore } from '@/store/song-store';
import { formatConfidence } from '@/utils/format';

const translateSchema = z.object({
  youtubeUrl: z
    .string()
    .min(1, 'Please enter a YouTube URL')
    .url('Please enter a valid URL')
    .refine(
      (url) => {
        try {
          const parsed = new URL(url);
          return parsed.hostname.includes('youtube.com') || parsed.hostname.includes('youtu.be');
        } catch {
          return false;
        }
      },
      { message: 'Must be a valid YouTube URL' },
    ),
  targetLanguage: z.string().min(1, 'Please select a target language'),
});

type TranslateFormData = z.infer<typeof translateSchema>;

const languageOptions = LANGUAGES.map((lang) => ({ value: lang, label: lang }));

/**
 * Dedicated Translate page.
 * Allows users to paste a YouTube URL and translate directly.
 */
export default function TranslatePage() {
  const router = useRouter();
  const ingestMutation = useIngestSong();
  const translateMutation = useTranslateSong();
  const currentSong = useSongStore((s) => s.currentSong);
  const [step, setStep] = useState<'input' | 'translating' | 'result'>('input');

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<TranslateFormData>({
    resolver: zodResolver(translateSchema),
    defaultValues: { youtubeUrl: '', targetLanguage: '' },
  });

  async function onSubmit(data: TranslateFormData) {
    setStep('translating');

    // Step 1: Ingest the song first
    ingestMutation.mutate(data.youtubeUrl, {
      onSuccess: (song) => {
        // Step 2: Translate
        translateMutation.mutate(
          { song_id: song.song_id, target_language: data.targetLanguage },
          {
            onSuccess: () => setStep('result'),
            onError: () => setStep('input'),
          },
        );
      },
      onError: () => setStep('input'),
    });
  }

  const isProcessing = ingestMutation.isPending || translateMutation.isPending;

  return (
    <>
      <PageHeader
        title="Translate"
        subtitle="Paste a YouTube link and select a language. We'll transcribe the song and deliver a literary translation that preserves the poetry."
      />

      <Container className="pb-20">
        {/* Form */}
        <FadeIn>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] p-8"
          >
            <div className="flex flex-col gap-6">
              <Input
                id="translate-url"
                label="YouTube URL"
                placeholder="https://www.youtube.com/watch?v=..."
                error={errors.youtubeUrl?.message}
                {...register('youtubeUrl')}
              />
              <Select
                id="translate-lang"
                label="Target Language"
                options={languageOptions}
                placeholder="Select a language"
                error={errors.targetLanguage?.message}
                {...register('targetLanguage')}
              />
              <PrimaryButton
                type="submit"
                isLoading={isProcessing}
                icon={<Languages className="h-4 w-4" />}
                size="lg"
                className="self-start"
              >
                {ingestMutation.isPending
                  ? 'Analyzing Song...'
                  : translateMutation.isPending
                    ? 'Translating...'
                    : 'Translate Song'}
              </PrimaryButton>
            </div>
          </form>
        </FadeIn>

        {/* Progress indicator */}
        {step === 'translating' && (
          <FadeIn className="mt-8">
            <div className="flex flex-col items-center gap-4 py-12 text-center">
              <div className="flex gap-2">
                <span className="h-2 w-2 rounded-full bg-[#F15C43] animate-bounce" />
                <span className="h-2 w-2 rounded-full bg-[#F15C43] animate-bounce [animation-delay:150ms]" />
                <span className="h-2 w-2 rounded-full bg-[#F15C43] animate-bounce [animation-delay:300ms]" />
              </div>
              <p className="text-[#8D8D8D]">
                {ingestMutation.isPending
                  ? 'Ingesting and analyzing the song...'
                  : 'Translating lyrics with literary precision...'}
              </p>
            </div>
          </FadeIn>
        )}

        {/* Translation result */}
        {step === 'result' && translateMutation.data && (
          <FadeIn className="mt-8">
            <div className="rounded-[16px] border border-[#F15C43]/20 bg-[#1B1B1B] p-8">
              {/* Header */}
              <div className="mb-6 flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-semibold text-[#F7F2E8] font-heading">
                    {currentSong?.title}
                  </h2>
                  <p className="text-sm text-[#8D8D8D] mt-1">
                    {currentSong?.artist} · Translated to{' '}
                    {translateMutation.data.target_language}
                  </p>
                </div>
                <Badge variant="accent">
                  {formatConfidence(translateMutation.data.confidence_score)} confidence
                </Badge>
              </div>

              {/* Lyrics */}
              <div className="whitespace-pre-wrap text-[#CFC8BE] leading-relaxed">
                {translateMutation.data.translated_lyrics}
              </div>

              {/* Notes */}
              {translateMutation.data.translation_notes && (
                <div className="mt-6 rounded-[12px] bg-[#222222] p-4">
                  <p className="text-xs font-medium tracking-wider text-[#8D8D8D] uppercase mb-2">
                    Translation Notes
                  </p>
                  <p className="text-sm text-[#CFC8BE]">
                    {translateMutation.data.translation_notes}
                  </p>
                </div>
              )}

              {/* Actions */}
              {currentSong && (
                <div className="mt-8 flex flex-wrap gap-3">
                  <SecondaryButton
                    icon={<ArrowRight className="h-4 w-4" />}
                    onClick={() => router.push(ROUTES.SONG(currentSong.song_id))}
                  >
                    View Full Song Details
                  </SecondaryButton>
                  <SecondaryButton
                    icon={<Search className="h-4 w-4" />}
                    onClick={() => {
                      setStep('input');
                      translateMutation.reset();
                    }}
                  >
                    Translate Another
                  </SecondaryButton>
                </div>
              )}
            </div>
          </FadeIn>
        )}
      </Container>
    </>
  );
}
