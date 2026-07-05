'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu } from 'lucide-react';
import { cn } from '@/lib/cn';
import { NAV_ITEMS, ROUTES } from '@/constants';
import { useScroll } from '@/hooks/use-scroll';
import { NavLink } from './nav-link';
import { MobileMenu } from './mobile-menu';
import { IconButton } from '@/components/buttons/icon-button';

/**
 * Sticky navbar.
 * Transparent initially, gains glass-morphism blur effect after scrolling.
 */
export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { scrolled } = useScroll(20);

  return (
    <>
      <header
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-500',
          scrolled
            ? 'glass shadow-[0_1px_0_rgba(255,255,255,0.06)]'
            : 'bg-transparent',
        )}
      >
        <nav
          className="mx-auto flex max-w-[1280px] items-center justify-between px-6 py-4 lg:px-8"
          aria-label="Main navigation"
        >
          {/* Logo */}
          <Link
            href={ROUTES.HOME}
            className="font-heading text-2xl font-bold tracking-tight text-[#F7F2E8] hover:text-[#F15C43] transition-colors duration-200"
          >
            SONUS
          </Link>

          {/* Desktop links */}
          <div className="hidden items-center gap-8 lg:flex">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.href} href={item.href} label={item.label} />
            ))}
          </div>

          {/* Mobile hamburger */}
          <div className="lg:hidden">
            <IconButton
              icon={<Menu className="h-5 w-5" />}
              label="Open menu"
              onClick={() => setMobileOpen(true)}
            />
          </div>
        </nav>
      </header>

      <MobileMenu isOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
    </>
  );
}
