'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: ReactNode;
  label: string;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Icon-only circular button with accessible aria-label.
 */
export function IconButton({
  icon,
  label,
  size = 'md',
  className,
  ...props
}: IconButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      aria-label={label}
      title={label}
      className={cn(
        'inline-flex items-center justify-center rounded-full',
        'text-[#8D8D8D] hover:text-[#F7F2E8] transition-colors duration-200',
        'hover:bg-[#222222]',
        {
          'h-8 w-8': size === 'sm',
          'h-10 w-10': size === 'md',
          'h-12 w-12': size === 'lg',
        },
        className,
      )}
      {...(props as React.ComponentPropsWithoutRef<typeof motion.button>)}
    >
      {icon}
    </motion.button>
  );
}
