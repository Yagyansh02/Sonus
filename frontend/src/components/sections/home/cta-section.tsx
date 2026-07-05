'use client';

import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { ROUTES } from '@/constants';
import { Container } from '@/components/layout/container';
import { Section } from '@/components/layout/section';
import { PrimaryButton } from '@/components/buttons/primary-button';
import { FadeIn } from '@/components/animations/fade-in';

/**
 * Bottom call-to-action section with accent-tinted background.
 */
export function CTASection() {
  return (
    <Section className="relative overflow-hidden">
      {/* Accent glow background */}
      <div className="pointer-events-none absolute inset-0">
        <div
          className="absolute left-1/2 top-1/2 h-[500px] w-[500px] rounded-full blur-[150px]"
          style={{
            background: 'rgba(241, 92, 67, 0.08)',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </div>

      <Container className="relative z-10">
        <FadeIn>
          <div className="flex flex-col items-center gap-8 text-center">
            <h2 className="font-heading max-w-2xl">
              Ready to Discover
              <br />
              What Music Really Means?
            </h2>
            <p className="text-lg text-muted max-w-lg">
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
  );
}
