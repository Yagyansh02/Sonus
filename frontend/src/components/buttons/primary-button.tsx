'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { Loader2 } from 'lucide-react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface PrimaryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isLoading?: boolean;
  icon?: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Primary accent CTA button with pill shape, hover lift, and loading spinner.
 */
export function PrimaryButton({
  children,
  isLoading,
  icon,
  size = 'md',
  className,
  disabled,
  ...props
}: PrimaryButtonProps) {
  return (
    <motion.button
      whileHover={!disabled && !isLoading ? { scale: 1.02, y: -2 } : undefined}
      whileTap={!disabled && !isLoading ? { scale: 0.98 } : undefined}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-full font-medium',
        'bg-[#F15C43] text-[#F7F2E8] transition-colors duration-200',
        'hover:bg-[#FF7B61] active:bg-[#e04d36]',
        'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#F15C43]',
        'shadow-[0_4px_16px_rgba(241,92,67,0.25)]',
        'hover:shadow-[0_8px_24px_rgba(241,92,67,0.35)]',
        {
          'px-4 py-2 text-sm': size === 'sm',
          'px-6 py-3 text-sm': size === 'md',
          'px-8 py-4 text-base': size === 'lg',
        },
        className,
      )}
      disabled={disabled || isLoading}
      {...(props as React.ComponentPropsWithoutRef<typeof motion.button>)}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        icon
      )}
      {children}
    </motion.button>
  );
}
