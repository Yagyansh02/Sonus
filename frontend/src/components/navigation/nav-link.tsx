'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/cn';

interface NavLinkProps {
  href: string;
  label: string;
  onClick?: () => void;
}

/**
 * Individual navigation link with active state styling.
 */
export function NavLink({ href, label, onClick }: NavLinkProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      href={href}
      onClick={onClick}
      className={cn(
        'relative text-sm font-medium transition-colors duration-200',
        isActive
          ? 'text-[#F7F2E8]'
          : 'text-[#8D8D8D] hover:text-[#CFC8BE]',
      )}
    >
      {label}
      {isActive && (
        <span className="absolute -bottom-1 left-0 h-0.5 w-full rounded-full bg-[#F15C43]" />
      )}
    </Link>
  );
}
