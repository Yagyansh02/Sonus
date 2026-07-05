'use client';

import { cn } from '@/lib/cn';
import type { ReactNode } from 'react';

interface Tab {
  id: string;
  label: string;
  icon?: ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (id: string) => void;
  className?: string;
}

/**
 * Horizontal tab navigation bar.
 * Renders pill-shaped active indicator with smooth transition.
 */
export function Tabs({ tabs, activeTab, onTabChange, className }: TabsProps) {
  return (
    <nav
      className={cn(
        'flex gap-1 rounded-full bg-[#181818] p-1 border border-[rgba(255,255,255,0.08)]',
        className,
      )}
      role="tablist"
      aria-label="Content tabs"
    >
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            aria-controls={`tabpanel-${tab.id}`}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium',
              'transition-all duration-300 whitespace-nowrap',
              isActive
                ? 'bg-[#F15C43] text-[#F7F2E8] shadow-lg'
                : 'text-[#8D8D8D] hover:text-[#CFC8BE] hover:bg-[#222222]',
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}
