import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  /** Accessible label for the spinner. */
  label?: string;
}

/**
 * Animated loading spinner.
 */
export function LoadingSpinner({
  size = 'md',
  className,
  label = 'Loading',
}: LoadingSpinnerProps) {
  return (
    <div
      className={cn('flex items-center justify-center', className)}
      role="status"
      aria-label={label}
    >
      <Loader2
        className={cn('animate-spin text-[#F15C43]', {
          'h-4 w-4': size === 'sm',
          'h-6 w-6': size === 'md',
          'h-10 w-10': size === 'lg',
        })}
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}
