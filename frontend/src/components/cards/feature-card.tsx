'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  className?: string;
}

/**
 * Feature highlight card for the landing page.
 * Uses CSS variables for GSAP scroll-driven theme transition.
 */
export function FeatureCard({ 
  icon, 
  title, 
  description, 
  className,
}: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 12px 40px rgba(0,0,0,0.4)' }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      style={{ 
        backgroundColor: 'var(--theme-card-bg, #1B1B1B)', 
        borderColor: 'var(--theme-card-border, rgba(255,255,255,0.08))' 
      }}
      className={cn(
        'flex flex-col gap-5 rounded-[16px] border',
        'p-8 transition-shadow duration-300',
        'shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        className,
      )}
    >
      <motion.div 
        style={{ 
          backgroundColor: 'var(--theme-icon-bg, rgba(241,92,67,0.1))', 
          color: 'var(--theme-icon-color, #F15C43)' 
        }}
        className="flex h-12 w-12 items-center justify-center rounded-[12px]"
      >
        {icon}
      </motion.div>
      <div className="flex flex-col gap-2">
        <motion.h3 
          style={{ color: 'var(--theme-title-color, #F7F2E8)' }} 
          className="text-xl font-semibold font-heading"
        >
          {title}
        </motion.h3>
        <motion.p 
          style={{ color: 'var(--theme-desc-color, #8D8D8D)' }} 
          className="text-sm leading-relaxed"
        >
          {description}
        </motion.p>
      </div>
    </motion.div>
  );
}
