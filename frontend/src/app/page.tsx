import { HeroSection } from '@/components/sections/home/hero-section';
import { FeaturesSection } from '@/components/sections/home/features-section';
import { HowItWorksSection } from '@/components/sections/home/how-it-works-section';
import { CTASection } from '@/components/sections/home/cta-section';
import { ScrollThemeProvider } from '@/components/sections/home/scroll-theme-provider';

/**
 * Home page — landing experience.
 *
 * ScrollThemeProvider mounts a single fixed backdrop and drives all
 * background-colour transitions via a centralised GSAP timeline.
 * Individual sections are transparent and inherit CSS variables for
 * content colours (text, card bg, etc.).
 */
export default function HomePage() {
  return (
    <ScrollThemeProvider>
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <CTASection />
    </ScrollThemeProvider>
  );
}
