'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { NAV_ITEMS } from '@/constants';
import { NavLink } from './nav-link';
import { IconButton } from '@/components/buttons/icon-button';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Full-screen mobile navigation overlay with slide-in animation.
 */
export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
            aria-hidden="true"
          />

          {/* Panel */}
          <motion.nav
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 z-50 flex h-full w-[280px] flex-col bg-[#0D0D0D] border-l border-[rgba(255,255,255,0.08)] p-8 lg:hidden"
            aria-label="Mobile navigation"
          >
            <div className="flex justify-end mb-8">
              <IconButton
                icon={<X className="h-5 w-5" />}
                label="Close menu"
                onClick={onClose}
              />
            </div>

            <div className="flex flex-col gap-6">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.href}
                  href={item.href}
                  label={item.label}
                  onClick={onClose}
                />
              ))}
            </div>
          </motion.nav>
        </>
      )}
    </AnimatePresence>
  );
}
