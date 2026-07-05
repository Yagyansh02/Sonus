import type { Metadata } from 'next';
import {
  Brain,
  Globe,
  Database,
  Cpu,
  Music2,
  Sparkles,
} from 'lucide-react';
import { PageHeader } from '@/components/layout/page-header';
import { Container } from '@/components/layout/container';
import { Section } from '@/components/layout/section';
import { FeatureCard } from '@/components/cards/feature-card';
import { FadeIn } from '@/components/animations/fade-in';
import { StaggerContainer, StaggerItem } from '@/components/animations/stagger-container';

export const metadata: Metadata = {
  title: 'About',
  description:
    'Learn about Sonus — a cultural song analysis engine powered by AI, graph databases, and a passion for understanding music across cultures.',
};

const TECH_STACK = [
  {
    icon: <Brain className="h-6 w-6" />,
    title: 'Groq LLM',
    description:
      'Lightning-fast inference with Llama 3.3 70B for cultural interpretation, genre classification, and literary translation.',
  },
  {
    icon: <Database className="h-6 w-6" />,
    title: 'Neo4j Graph Database',
    description:
      'Songs, artists, genres, cultural themes, and translations stored as a rich knowledge graph with vector search capabilities.',
  },
  {
    icon: <Cpu className="h-6 w-6" />,
    title: 'RAG Pipeline',
    description:
      'Retrieval-Augmented Generation using HuggingFace embeddings for contextual, grounded answers about any song.',
  },
  {
    icon: <Globe className="h-6 w-6" />,
    title: 'Literary Translation',
    description:
      'Not just word-for-word — we preserve poetic meaning, metaphors, and cultural references across 20+ languages.',
  },
  {
    icon: <Music2 className="h-6 w-6" />,
    title: 'Audio Intelligence',
    description:
      'Automatic transcription from YouTube with ElevenLabs fallback for accurate lyrics extraction in any language.',
  },
  {
    icon: <Sparkles className="h-6 w-6" />,
    title: 'Cultural Analysis',
    description:
      'AI-powered ethnomusicological analysis that explains slang, cultural references, emotional context, and artist intent.',
  },
] as const;

/**
 * About page — mission, technology, and brand story.
 */
export default function AboutPage() {
  return (
    <>
      <PageHeader
        title="About Sonus"
        subtitle="A cultural song analysis engine built to bridge the gap between languages, cultures, and the music that moves us."
      />

      {/* Mission */}
      <Section className="pt-0">
        <Container>
          <FadeIn>
            <div className="grid gap-12 lg:grid-cols-2 items-center">
              <div className="flex flex-col gap-6">
                <span className="text-sm font-medium tracking-wider text-[#F15C43] uppercase">
                  Our Mission
                </span>
                <h2 className="font-heading">
                  Music is Universal.
                  <br />
                  Understanding Should Be Too.
                </h2>
                <p className="text-[#8D8D8D] leading-relaxed">
                  Every song carries layers of meaning — cultural references, 
                  poetic devices, emotional context, and historical significance 
                  that transcend language. Sonus uses AI to unlock these layers, 
                  making every song in the world accessible to everyone.
                </p>
                <p className="text-[#8D8D8D] leading-relaxed">
                  Whether it&apos;s a Bollywood classic, a K-pop anthem, a Latin 
                  reggaeton hit, or an underground hip-hop track — Sonus helps 
                  you understand not just the words, but the world behind them.
                </p>
              </div>

              {/* Decorative accent block */}
              <div className="relative flex items-center justify-center">
                <div className="relative h-80 w-full max-w-md rounded-[16px] border border-[rgba(255,255,255,0.08)] bg-[#1B1B1B] p-8 flex items-center justify-center overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-[#F15C43]/5 to-transparent" />
                  <span className="relative font-heading text-6xl font-bold text-[#F7F2E8]/10 select-none">
                    SONUS
                  </span>
                </div>
              </div>
            </div>
          </FadeIn>
        </Container>
      </Section>

      {/* Tech Stack */}
      <Section className="bg-[#181818]/50">
        <Container>
          <FadeIn className="mb-16 text-center">
            <span className="text-sm font-medium tracking-wider text-[#F15C43] uppercase">
              Under the Hood
            </span>
            <h2 className="mt-4 font-heading">
              Built with Cutting-Edge
              <br />
              Technology
            </h2>
          </FadeIn>

          <StaggerContainer className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {TECH_STACK.map((tech) => (
              <StaggerItem key={tech.title}>
                <FeatureCard
                  icon={tech.icon}
                  title={tech.title}
                  description={tech.description}
                />
              </StaggerItem>
            ))}
          </StaggerContainer>
        </Container>
      </Section>
    </>
  );
}
