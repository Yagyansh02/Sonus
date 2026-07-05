'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { fadeIn } from './motion-variants';
import type { ReactNode } from 'react';

interface FadeInProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  /** Delay before animation starts (seconds). */
  delay?: number;
  className?: string;
}

/**
 * Wrapper that fades content in with a subtle upward slide.
 * Triggers when the element enters the viewport.
 */
export function FadeIn({ children, delay = 0, className, ...props }: FadeInProps) {
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-80px' }}
      transition={{ delay }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}
