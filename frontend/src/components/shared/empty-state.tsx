import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}

/**
 * Empty state display with icon, message, and optional action button.
 */
export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-4 rounded-[16px]',
        'border border-dashed border-[rgba(255,255,255,0.08)] bg-[#181818]',
        'px-8 py-16 text-center',
        className,
      )}
    >
      <div className="text-[#8D8D8D]">{icon}</div>
      <div className="flex flex-col gap-1">
        <h3 className="text-lg font-semibold text-[#F7F2E8] font-heading">
          {title}
        </h3>
        <p className="text-sm text-[#8D8D8D] max-w-sm">{description}</p>
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
