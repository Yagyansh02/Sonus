import { HeroSection } from '@/components/sections/home/hero-section';
import { FeaturesSection } from '@/components/sections/home/features-section';
import { HowItWorksSection } from '@/components/sections/home/how-it-works-section';
import { CTASection } from '@/components/sections/home/cta-section';

/**
 * Home page — landing experience.
 * Composes hero, features, how-it-works, and CTA sections.
 */
export default function HomePage() {
  return (
    <>
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
    </>
  );
}
