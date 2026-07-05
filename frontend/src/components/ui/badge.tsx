import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface BadgeProps {
  children: ReactNode;
  /** Visual variant. */
  variant?: 'default' | 'accent' | 'outline';
  className?: string;
}

/**
 * Small pill badge for genres, themes, moods, and metadata labels.
 */
export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-3 py-1 text-xs font-medium tracking-wide',
        {
          'bg-[#222222] text-[#CFC8BE]': variant === 'default',
          'bg-[#F15C43]/15 text-[#F15C43]': variant === 'accent',
          'border border-[rgba(255,255,255,0.08)] text-[#8D8D8D]': variant === 'outline',
        },
        className,
      )}
    >
      {children}
    </span>
  );
}
