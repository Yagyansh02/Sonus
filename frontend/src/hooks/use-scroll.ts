'use client';

import { useEffect, useState } from 'react';

/**
 * Tracks the window scroll position.
 * Returns `scrolled = true` once the user scrolls past `threshold` pixels.
 */
export function useScroll(threshold: number = 20) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > threshold);
    }

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [threshold]);

  return { scrolled };
}
