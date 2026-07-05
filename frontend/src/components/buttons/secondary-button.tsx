'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import { Loader2 } from 'lucide-react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface SecondaryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isLoading?: boolean;
  icon?: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Ghost / outline variant button with subtle border and hover fill.
 */
export function SecondaryButton({
  children,
  isLoading,
  icon,
  size = 'md',
  className,
  disabled,
  ...props
}: SecondaryButtonProps) {
  return (
    <motion.button
      whileHover={!disabled && !isLoading ? { scale: 1.02, y: -1 } : undefined}
      whileTap={!disabled && !isLoading ? { scale: 0.98 } : undefined}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-full font-medium',
        'border border-[rgba(255,255,255,0.08)] text-[#CFC8BE]',
        'bg-transparent transition-all duration-200',
        'hover:bg-[#222222] hover:text-[#F7F2E8] hover:border-[rgba(255,255,255,0.15)]',
        'disabled:opacity-50 disabled:cursor-not-allowed',
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
