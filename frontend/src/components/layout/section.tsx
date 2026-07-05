import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface SectionProps {
  children: ReactNode;
  className?: string;
  id?: string;
}

/**
 * Section wrapper with consistent vertical padding.
 * Responsive: 120px desktop → 80px tablet → 48px mobile.
 */
export function Section({ children, className, id }: SectionProps) {
  return (
    <section
      id={id}
      className={cn(
        'py-12 md:py-20 lg:py-[120px]',
        className,
      )}
    >
      {children}
    </section>
  );
}
