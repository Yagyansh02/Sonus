import { cn } from '@/lib/cn';

interface SkeletonProps {
  className?: string;
}

/**
 * Animated skeleton placeholder for loading states.
 * Apply width/height via className.
 */
export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-[16px] bg-[#222222]',
        className,
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
