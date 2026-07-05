import { forwardRef, type SelectHTMLAttributes } from 'react';
import { cn } from '@/lib/cn';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  error?: string;
  label?: string;
  options: readonly { value: string; label: string }[];
  placeholder?: string;
}

/**
 * Styled select dropdown with optional label and error state.
 */
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, error, label, options, placeholder, id, ...props }, ref) => {
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
        <select
          ref={ref}
          id={id}
          className={cn(
            'w-full rounded-[12px] border bg-[#1B1B1B] px-4 py-3 text-[#F7F2E8]',
            'transition-all duration-200 appearance-none cursor-pointer',
            'focus:outline-none focus:ring-2 focus:ring-[#F15C43]/50 focus:border-[#F15C43]',
            error
              ? 'border-red-500/50'
              : 'border-[rgba(255,255,255,0.08)]',
            className,
          )}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {error && (
          <p className="text-xs text-red-400" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  },
);

Select.displayName = 'Select';
