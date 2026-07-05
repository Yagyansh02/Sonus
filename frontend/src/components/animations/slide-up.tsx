'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { slideUp } from './motion-variants';
import type { ReactNode } from 'react';

interface SlideUpProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  delay?: number;
  className?: string;
}

/**
 * Wrapper that slides content up with a fade-in effect.
 * More dramatic than FadeIn — use for hero sections and primary content.
 */
export function SlideUp({ children, delay = 0, className, ...props }: SlideUpProps) {
  return (
    <motion.div
      variants={slideUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-60px' }}
      transition={{ delay }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}
