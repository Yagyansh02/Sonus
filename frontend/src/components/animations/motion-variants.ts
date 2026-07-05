import type { Variants } from 'framer-motion';
import { DURATION, EASING } from '@/constants';

/**
 * Reusable Framer Motion animation variants.
 * Import and spread into `<motion.div variants={fadeIn} ...>`.
 */

export const fadeIn: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.slow, ease: EASING.smooth },
  },
};

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: EASING.smooth },
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: DURATION.normal, ease: EASING.smooth },
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: DURATION.normal, ease: EASING.smooth },
  },
};

/** Hover variants for interactive cards. */
export const cardHover = {
  rest: { y: 0, boxShadow: '0 4px 24px rgba(0,0,0,0.2)' },
  hover: {
    y: -4,
    boxShadow: '0 12px 40px rgba(0,0,0,0.4)',
    transition: { duration: DURATION.fast, ease: EASING.smooth },
  },
};
