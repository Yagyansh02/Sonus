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
 * Dark card with icon, heading, and description.
 */
export function FeatureCard({ icon, title, description, className }: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
      className={cn(
        'flex flex-col gap-5 rounded-[16px] border border-[rgba(255,255,255,0.08)]',
        'bg-[#1B1B1B] p-8 transition-shadow duration-300',
        'shadow-[0_4px_24px_rgba(0,0,0,0.2)]',
        'hover:shadow-[0_12px_40px_rgba(0,0,0,0.4)]',
        'hover:border-[rgba(255,255,255,0.12)]',
        className,
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-[12px] bg-[#F15C43]/10 text-[#F15C43]">
        {icon}
      </div>
      <div className="flex flex-col gap-2">
        <h3 className="text-xl font-semibold text-[#F7F2E8] font-heading">
          {title}
        </h3>
        <p className="text-sm leading-relaxed text-[#8D8D8D]">
          {description}
        </p>
      </div>
    </motion.div>
  );
}
