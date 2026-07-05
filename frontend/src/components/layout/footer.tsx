import Link from 'next/link';
import { Container } from './container';
import { NAV_ITEMS } from '@/constants';

/**
 * Minimal dark footer with navigation links and copyright.
 */
export function Footer() {
  return (
    <footer className="border-t border-[rgba(255,255,255,0.08)] bg-[#0D0D0D]">
      <Container className="py-16 lg:py-20">
        <div className="flex flex-col items-center gap-10 lg:flex-row lg:justify-between lg:items-start">
          {/* Brand */}
          <div className="flex flex-col items-center gap-3 lg:items-start">
            <span className="font-heading text-2xl font-bold text-[#F7F2E8]">
              SONUS
            </span>
            <p className="text-sm text-[#8D8D8D] max-w-[280px] text-center lg:text-left">
              Cultural song analysis & interpretation engine. Understand the music that moves the world.
            </p>
          </div>

          {/* Links */}
          <nav
            className="flex flex-wrap justify-center gap-8"
            aria-label="Footer navigation"
          >
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-sm text-[#8D8D8D] hover:text-[#CFC8BE] transition-colors duration-200"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Divider & copyright */}
        <div className="mt-12 border-t border-[rgba(255,255,255,0.06)] pt-8 text-center">
          <p className="text-xs text-[#8D8D8D]">
            © {new Date().getFullYear()} Sonus. All rights reserved.
          </p>
        </div>
      </Container>
    </footer>
  );
}
