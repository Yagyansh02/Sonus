'use client';

import { motion, type HTMLMotionProps } from 'framer-motion';
import { staggerContainer, staggerItem } from './motion-variants';
import type { ReactNode } from 'react';

interface StaggerContainerProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  className?: string;
}

/**
 * Container that staggers the entrance animation of its children.
 * Each direct child should be a <StaggerItem />.
 */
export function StaggerContainer({ children, className, ...props }: StaggerContainerProps) {
  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-60px' }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

interface StaggerItemProps extends Omit<HTMLMotionProps<'div'>, 'children'> {
  children: ReactNode;
  className?: string;
}

/**
 * Individual item within a StaggerContainer.
 * Animates in sequence based on the parent's stagger delay.
 */
export function StaggerItem({ children, className, ...props }: StaggerItemProps) {
  return (
    <motion.div variants={staggerItem} className={className} {...props}>
      {children}
    </motion.div>
  );
}
