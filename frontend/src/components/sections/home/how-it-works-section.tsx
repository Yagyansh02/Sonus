'use client';

import { Link2, FileSearch, Sparkles, Globe } from 'lucide-react';
import { Container } from '@/components/layout/container';
import { Section } from '@/components/layout/section';
import { FadeIn } from '@/components/animations/fade-in';
import { StaggerContainer, StaggerItem } from '@/components/animations/stagger-container';

const STEPS = [
  {
    number: '01',
    icon: <Link2 className="h-5 w-5" />,
    title: 'Paste a YouTube Link',
    description: 'Drop any YouTube URL — any language, any genre, any era.',
  },
  {
    number: '02',
    icon: <FileSearch className="h-5 w-5" />,
    title: 'AI Processes the Song',
    description:
      'We extract metadata, transcribe lyrics, classify genres and themes, and build a knowledge graph.',
  },
  {
    number: '03',
    icon: <Globe className="h-5 w-5" />,
    title: 'Translate Across Cultures',
    description:
      'Literary translation that preserves the poetry — not just the words.',
  },
  {
    number: '04',
    icon: <Sparkles className="h-5 w-5" />,
    title: 'Ask Anything',
    description:
      "Have a conversation with AI about the song's meaning, cultural references, and hidden layers.",
  },
] as const;

/**
 * Step-by-step visual flow showing how Sonus works.
 */
export function HowItWorksSection() {
  return (
    <Section>
      <Container>
        <FadeIn className="mb-16 text-center">
          <span className="text-sm font-medium tracking-wider text-accent uppercase">
            How It Works
          </span>
          <h2 className="mt-4 font-heading">
            From Link to Understanding
            <br />
            in Seconds
          </h2>
        </FadeIn>

        <StaggerContainer className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step) => (
            <StaggerItem key={step.number}>
              <div className="flex flex-col gap-4">
                {/* Step number + icon */}
                <div className="flex items-center gap-3">
                  <span className="font-heading text-3xl font-bold text-accent/20">
                    {step.number}
                  </span>
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-surface text-accent">
                    {step.icon}
                  </div>
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-primary-text font-heading">
                  {step.title}
                </h3>
                <p className="text-sm leading-relaxed text-muted">
                  {step.description}
                </p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </Container>
    </Section>
  );
}
