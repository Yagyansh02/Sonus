import { AlertTriangle } from 'lucide-react';
import { SecondaryButton } from '@/components/buttons/secondary-button';
import { cn } from '@/lib/cn';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

/**
 * Error state display with message and retry button.
 */
export function ErrorState({
  message = 'Something went wrong. Please try again.',
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-4 rounded-[16px]',
        'border border-red-500/20 bg-red-500/5',
        'px-8 py-16 text-center',
        className,
      )}
      role="alert"
    >
      <AlertTriangle className="h-10 w-10 text-red-400" />
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[#F7F2E8] font-heading">
          Error
        </h3>
        <p className="text-sm text-[#8D8D8D] max-w-sm">{message}</p>
      </div>
      {onRetry && (
        <SecondaryButton onClick={onRetry} size="sm">
          Try Again
        </SecondaryButton>
      )}
    </div>
  );
}
