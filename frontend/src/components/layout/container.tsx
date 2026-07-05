import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface ContainerProps {
  children: ReactNode;
  className?: string;
  /** HTML element to render as. */
  as?: 'div' | 'section' | 'main' | 'article';
}

/**
 * Max-width centered container.
 * Standard content wrapper used across all pages.
 */
export function Container({
  children,
  className,
  as: Component = 'div',
}: ContainerProps) {
  return (
    <Component
      className={cn('mx-auto w-full max-w-[1280px] px-6 lg:px-8', className)}
    >
      {children}
    </Component>
  );
}
