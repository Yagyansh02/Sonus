'use client';

import { useRef, useEffect, useState } from 'react';
import type { MouseEvent } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './gooey-nav.css';

export interface GooeyNavItem {
  label: string;
  href: string;
}

interface GooeyNavProps {
  items: readonly GooeyNavItem[];
  animationTime?: number;
  particleCount?: number;
  particleDistances?: [number, number];
  particleR?: number;
  timeVariance?: number;
  /** Particle burst colors (hex). Defaults to brand orange. */
  colors?: string[];
}

// ─── Pure helpers (outside component to avoid re-creation on each render) ──────

const noise = (n = 1) => n / 2 - Math.random() * n;

const getXY = (distance: number, pointIndex: number, totalPoints: number) => {
  const angle = ((360 + noise(8)) / totalPoints) * pointIndex * (Math.PI / 180);
  return [distance * Math.cos(angle), distance * Math.sin(angle)] as const;
};

const buildParticleData = (
  i: number,
  t: number,
  d: [number, number],
  r: number,
  particleCount: number,
  colors: string[],
) => {
  const rotate = noise(r / 10);
  return {
    start: getXY(d[0], particleCount - i, particleCount),
    end: getXY(d[1] + noise(7), particleCount - i, particleCount),
    time: t,
    scale: 1 + noise(0.2),
    color: colors[Math.floor(Math.random() * colors.length)],
    rotate: rotate > 0 ? (rotate + r / 20) * 10 : (rotate - r / 20) * 10,
  };
};

// ─── Component ─────────────────────────────────────────────────────────────────

export function GooeyNav({
  items,
  animationTime = 600,
  particleCount = 15,
  particleDistances = [90, 10],
  particleR = 100,
  timeVariance = 300,
  colors = ['#F15C43'],
}: GooeyNavProps) {
  const pathname = usePathname();
  const initialIndex = items.findIndex((item) => item.href === pathname);

  const containerRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLUListElement>(null);
  /** Positioned absolutely over the active <li>; receives gooey particle bursts. */
  const burstRef = useRef<HTMLSpanElement>(null);

  const [activeIndex, setActiveIndex] = useState(initialIndex);

  // ── Particle burst ────────────────────────────────────────────────────────

  const spawnParticles = (target: HTMLElement) => {
    const burst = burstRef.current;
    if (!burst) return;

    // Position the burst layer exactly over the target <li>
    const containerRect = containerRef.current!.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    burst.style.left = `${targetRect.x - containerRect.x}px`;
    burst.style.top = `${targetRect.y - containerRect.y}px`;
    burst.style.width = `${targetRect.width}px`;
    burst.style.height = `${targetRect.height}px`;

    // Clear previous particles
    burst.querySelectorAll('.particle').forEach((p) => burst.removeChild(p));

    const d = particleDistances;
    const r = particleR;
    const bubbleTime = animationTime * 2 + timeVariance;
    burst.style.setProperty('--time', `${bubbleTime}ms`);

    burst.classList.remove('active');

    for (let i = 0; i < particleCount; i++) {
      const t = animationTime * 2 + noise(timeVariance * 2);
      const p = buildParticleData(i, t, d, r, particleCount, colors);

      setTimeout(() => {
        const particle = document.createElement('span');
        const point = document.createElement('span');

        particle.classList.add('particle');
        particle.style.setProperty('--start-x', `${p.start[0]}px`);
        particle.style.setProperty('--start-y', `${p.start[1]}px`);
        particle.style.setProperty('--end-x', `${p.end[0]}px`);
        particle.style.setProperty('--end-y', `${p.end[1]}px`);
        particle.style.setProperty('--time', `${p.time}ms`);
        particle.style.setProperty('--scale', `${p.scale}`);
        particle.style.setProperty('--color', p.color);
        particle.style.setProperty('--rotate', `${p.rotate}deg`);

        point.classList.add('point');
        particle.appendChild(point);
        burst.appendChild(particle);

        requestAnimationFrame(() => burst.classList.add('active'));

        setTimeout(() => {
          try {
            burst.removeChild(particle);
          } catch {
            // particle may already be gone
          }
        }, t);
      }, 30);
    }
  };

  // ── Interactions ──────────────────────────────────────────────────────────

  const activateLi = (index: number, liEl: HTMLElement) => {
    setActiveIndex(index);
    spawnParticles(liEl);
  };

  const handleClick = (e: MouseEvent<HTMLAnchorElement>, index: number) => {
    const liEl = e.currentTarget.parentElement;
    if (!liEl || activeIndex === index) return;
    activateLi(index, liEl);
  };

  // ── Sync active index with pathname changes ───────────────────────────────

  useEffect(() => {
    const idx = items.findIndex((item) => item.href === pathname);

    if (idx >= 0 && idx !== activeIndex) {
      const liEl = navRef.current?.querySelectorAll('li')[idx];
      if (liEl) activateLi(idx, liEl as HTMLElement);
    } else if (idx === -1 && activeIndex !== -1) {
      setActiveIndex(-1);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname, items]);

  // ── Reposition on resize / font load ─────────────────────────────────────

  useEffect(() => {
    if (!navRef.current) return;

    const repositionBurst = () => {
      if (activeIndex < 0) return;
      const liEl = navRef.current?.querySelectorAll('li')[activeIndex];
      if (liEl && burstRef.current && containerRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const targetRect = liEl.getBoundingClientRect();
        burstRef.current.style.left = `${targetRect.x - containerRect.x}px`;
        burstRef.current.style.top = `${targetRect.y - containerRect.y}px`;
        burstRef.current.style.width = `${targetRect.width}px`;
        burstRef.current.style.height = `${targetRect.height}px`;
      }
    };

    document.fonts?.ready.then(repositionBurst);

    const ro = new ResizeObserver(repositionBurst);
    ro.observe(navRef.current);
    return () => ro.disconnect();
  }, [activeIndex]);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="gooey-nav-container" ref={containerRef}>
      {/* Invisible SVG filter definition for gooey particle effect */}
      <svg width="0" height="0" aria-hidden="true" style={{ position: 'absolute', pointerEvents: 'none' }}>
        <defs>
          <filter id="gooey-burst-filter">
            <feGaussianBlur in="SourceGraphic" stdDeviation="7" result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -9"
              result="gooey"
            />
            <feComposite in="SourceGraphic" in2="gooey" operator="atop" />
          </filter>
        </defs>
      </svg>

      <nav>
        <ul ref={navRef}>
          {items.map((item, index) => (
            <li key={item.href} className={activeIndex === index ? 'active' : ''}>
              <Link href={item.href} onClick={(e) => handleClick(e, index)}>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Particle burst layer — purely decorative, never covers nav text */}
      <span className="gooey-burst" ref={burstRef} aria-hidden="true" />
    </div>
  );
}
