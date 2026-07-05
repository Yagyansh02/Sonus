import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cn } from '@/lib/cn';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: string;
  label?: string;
}

/**
 * Styled textarea with optional label and error state.
 */
export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, label, id, ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2">
        {label && (
          <label
            htmlFor={id}
            className="text-sm font-medium text-[#CFC8BE]"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={id}
          className={cn(
            'w-full rounded-[12px] border bg-[#1B1B1B] px-4 py-3 text-[#F7F2E8]',
            'placeholder:text-[#8D8D8D] transition-all duration-200 resize-none',
            'focus:outline-none focus:ring-2 focus:ring-[#F15C43]/50 focus:border-[#F15C43]',
            error
              ? 'border-red-500/50'
              : 'border-[rgba(255,255,255,0.08)]',
            className,
          )}
          {...props}
        />
        {error && (
          <p className="text-xs text-red-400" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Textarea.displayName = 'Textarea';
