import { FadeIn } from '@/components/animations/fade-in';
import { Container } from './container';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
}

/**
 * Reusable page header with large editorial title and optional subtitle.
 * Includes top padding to account for the fixed navbar.
 */
export function PageHeader({ title, subtitle }: PageHeaderProps) {
  return (
    <div className="pt-32 pb-12 md:pt-40 md:pb-16 lg:pt-44 lg:pb-20">
      <Container>
        <FadeIn>
          <div className="flex flex-col gap-4 max-w-2xl">
            <h1 className="font-heading">{title}</h1>
            {subtitle && (
              <p className="text-lg text-[#8D8D8D] leading-relaxed">
                {subtitle}
              </p>
            )}
          </div>
        </FadeIn>
      </Container>
    </div>
  );
}
