'use client';

import { FileText, Languages, MessageCircle } from 'lucide-react';
import { Container } from '@/components/layout/container';
import { Section } from '@/components/layout/section';
import { FeatureCard } from '@/components/cards/feature-card';
import { FadeIn } from '@/components/animations/fade-in';
import { StaggerContainer, StaggerItem } from '@/components/animations/stagger-container';

const FEATURES = [
  {
    icon: <FileText className="h-6 w-6" />,
    title: 'Transcribe',
    description:
      'Extract accurate lyrics from any YouTube video. Our pipeline handles multiple languages with automatic fallback to ensure no words are lost.',
  },
  {
    icon: <Languages className="h-6 w-6" />,
    title: 'Translate',
    description:
      'Literary localization that preserves poetic meaning, metaphors, and cultural references — not just word-for-word translation.',
  },
  {
    icon: <MessageCircle className="h-6 w-6" />,
    title: 'Interpret',
    description:
      'Ask questions about any song. Our AI explains slang, cultural references, emotional context, and artist intent like an ethnomusicologist.',
  },
] as const;

/**
 * Three-column feature grid highlighting the core capabilities.
 *
 * The background is controlled by <ScrollThemeProvider> in page.tsx.
 * This component places two invisible sentinel <div>s that act as
 * ScrollTrigger anchors:
 *   data-theme-trigger="light"  — starts dark→orange transition
 *   data-theme-trigger="dark"   — starts orange→dark transition
 */
export function FeaturesSection() {
  return (
    <div className="relative w-full">
      {/* Sentinel: start of orange theme zone */}
      <div data-theme-trigger="light" aria-hidden="true" />

      <Section className="bg-transparent relative z-10">
        <Container>
          <FadeIn className="mb-16 text-center">
            <span
              className="text-sm font-medium tracking-wider uppercase inline-block"
              style={{ color: 'var(--theme-sub-color, #F15C43)' }}
            >
              Capabilities
            </span>
            <h2
              className="mt-4 font-heading text-4xl md:text-5xl lg:text-6xl"
              style={{ color: 'var(--theme-title-color, #F7F2E8)' }}
            >
              Three Pillars of
              <br />
              Musical Understanding
            </h2>
          </FadeIn>

          <StaggerContainer className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((feature) => (
              <StaggerItem key={feature.title}>
                <FeatureCard
                  icon={feature.icon}
                  title={feature.title}
                  description={feature.description}
                />
              </StaggerItem>
            ))}
          </StaggerContainer>
        </Container>
      </Section>

      {/* Sentinel: end of orange theme zone — placed after the section content */}
      <div data-theme-trigger="dark" aria-hidden="true" />
    </div>
  );
}
