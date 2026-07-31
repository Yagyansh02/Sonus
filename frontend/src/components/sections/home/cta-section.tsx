'use client';

import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { ROUTES } from '@/constants';
import { Container } from '@/components/layout/container';
import { Section } from '@/components/layout/section';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { FadeIn } from '@/components/animations/fade-in';

/**
 * Bottom call-to-action section.
 * Transitions dark → orange as it enters the viewport via ScrollThemeProvider.
 * Text colours are driven by CSS variables so they invert automatically.
 */
export function CTASection() {
  return (
    <div className="relative w-full">
      {/* Sentinel: ScrollThemeProvider listens for this to start dark→orange */}
      <div data-theme-trigger="cta-light" aria-hidden="true" />

      <Section className="relative overflow-hidden bg-transparent">
        <Container className="relative z-10">
          <FadeIn>
            <div className="flex flex-col items-center gap-8 text-center">
              <h2
                className="font-heading max-w-2xl"
                style={{ color: 'var(--theme-title-color, #F7F2E8)' }}
              >
                Ready to Discover
                <br />
                What Music Really Means?
              </h2>
              <p
                className="text-lg max-w-lg"
                style={{ color: 'var(--theme-desc-color, #8D8D8D)' }}
              >
                Paste a YouTube link and let Sonus reveal the cultural depth
                hidden within every song.
              </p>
              <Link href={ROUTES.EXPLORE}>
                <PrimaryButton size="lg" icon={<ArrowRight className="h-4 w-4" />}>
                  Start Now
                </PrimaryButton>
              </Link>
            </div>
          </FadeIn>
        </Container>
      </Section>
    </div>
  );
}
