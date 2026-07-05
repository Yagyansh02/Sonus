'use client';

import { useState } from 'react';
import { Languages } from 'lucide-react';
import { LANGUAGES } from '@/constants';
import { useTranslateSong, useTranslations } from '@/hooks/use-translation';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { Select } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/shared/loading-spinner';
import { ErrorState } from '@/components/shared/error-state';
import { EmptyState } from '@/components/shared/empty-state';
import { FadeIn } from '@/components/animations/fade-in';
import { formatConfidence } from '@/utils/format';

interface TranslationTabProps {
  songId: string;
}

const languageOptions = LANGUAGES.map((lang) => ({
  value: lang,
  label: lang,
}));

/**
 * Translation tab with language selector, translate action, and translations list.
 */
export function TranslationTab({ songId }: TranslationTabProps) {
  const [targetLang, setTargetLang] = useState('');
  const translateMutation = useTranslateSong();
  const { data: translationsList, isLoading, isError, error, refetch } = useTranslations(songId);

  function handleTranslate() {
    if (!targetLang) return;
    translateMutation.mutate({ song_id: songId, target_language: targetLang });
  }

  return (
    <div
      className="flex flex-col gap-8"
      role="tabpanel"
      id="tabpanel-translation"
    >
      {/* Translation form */}
      <FadeIn>
        <div className="rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] p-8">
          <h3 className="text-lg font-semibold text-[#F7F2E8] mb-6 font-heading">
            Translate Lyrics
          </h3>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <Select
                id="target-language"
                label="Target Language"
                options={languageOptions}
                placeholder="Select a language"
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
              />
            </div>
            <PrimaryButton
              onClick={handleTranslate}
              isLoading={translateMutation.isPending}
              disabled={!targetLang}
              icon={<Languages className="h-4 w-4" />}
            >
              {translateMutation.isPending ? 'Translating...' : 'Translate'}
            </PrimaryButton>
          </div>
        </div>
      </FadeIn>

      {/* Active translation result */}
      {translateMutation.data && (
        <FadeIn>
          <div className="rounded-[16px] border border-[#F15C43]/20 bg-[#1B1B1B] p-8">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-[#F7F2E8] font-heading">
                {translateMutation.data.target_language} Translation
              </h3>
              <Badge variant="accent">
                {formatConfidence(translateMutation.data.confidence_score)} confidence
              </Badge>
            </div>
            <div className="whitespace-pre-wrap text-[#CFC8BE] leading-relaxed">
              {translateMutation.data.translated_lyrics}
            </div>
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
          </div>
        </FadeIn>
      )}

      {/* Existing translations list */}
      <div>
        <h3 className="text-lg font-semibold text-[#F7F2E8] mb-4 font-heading">
          All Translations
        </h3>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner label="Loading translations" />
          </div>
        ) : isError ? (
          <ErrorState
            message={error?.message || 'Failed to load translations'}
            onRetry={() => refetch()}
          />
        ) : !translationsList?.translations.length ? (
          <EmptyState
            icon={<Languages className="h-10 w-10" />}
            title="No Translations Yet"
            description="Translate this song into another language to see results here."
          />
        ) : (
          <div className="flex flex-col gap-4">
            {translationsList.translations.map((t) => (
              <details
                key={t.translation_id}
                className="group rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] overflow-hidden"
              >
                <summary className="flex cursor-pointer items-center justify-between p-6 hover:bg-[#222222] transition-colors">
                  <div className="flex items-center gap-3">
                    <Badge variant="default">{t.target_language}</Badge>
                    <span className="text-sm text-[#8D8D8D]">
                      {formatConfidence(t.confidence_score)} confidence
                    </span>
                  </div>
                </summary>
                <div className="border-t border-[rgba(255,255,255,0.06)] p-6">
                  <div className="whitespace-pre-wrap text-[#CFC8BE] leading-relaxed text-sm">
                    {t.translated_lyrics}
                  </div>
                  {t.translation_notes && (
                    <div className="mt-4 rounded-[12px] bg-[#222222] p-4">
                      <p className="text-xs font-medium tracking-wider text-[#8D8D8D] uppercase mb-1">
                        Notes
                      </p>
                      <p className="text-sm text-[#CFC8BE]">{t.translation_notes}</p>
                    </div>
                  )}
                </div>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
