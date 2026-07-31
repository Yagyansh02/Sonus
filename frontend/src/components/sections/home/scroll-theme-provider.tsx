'use client';

/**
 * ScrollThemeProvider
 *
 * Single source of truth for the page background color on the home page.
 * Uses a GSAP ScrollTrigger timeline that directly interpolates between
 * named colour stops — so there is NEVER an intermediate default/black frame,
 * even on very fast scrolling or keyboard navigation.
 *
 * Strategy (Handshake-style):
 *  - One fixed <div> covers the full viewport and holds the background.
 *  - GSAP animates its `backgroundColor` along a scrubbed timeline whose
 *    trigger points are the data-theme-trigger elements rendered in the DOM.
 *  - Sections themselves remain transparent; only their *content* colours
 *    change via CSS variables set on the fixed layer and inherited down.
 */

import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import type { ReactNode } from 'react';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

// ─── Colour palette ─────────────────────────────────────────────────────────
const DARK = {
  bg: '#0D0D0D',
  titleColor: '#F7F2E8',
  subColor: '#F15C43',
  cardBg: '#1B1B1B',
  cardBorder: 'rgba(255,255,255,0.08)',
  descColor: '#8D8D8D',
  iconBg: 'rgba(241,92,67,0.1)',
  iconColor: '#F15C43',
} as const;

const LIGHT = {
  bg: '#F15C43',
  titleColor: '#000000',
  subColor: '#000000',
  cardBg: '#F7F2E8',
  cardBorder: 'rgba(0,0,0,0.05)',
  descColor: 'rgba(0,0,0,0.7)',
  iconBg: 'rgba(241,92,67,0.15)',
  iconColor: '#F15C43',
} as const;

// ─── Helper — set CSS variables on the backdrop element ────────────────────
function applyVars(el: HTMLElement, theme: typeof DARK) {
  el.style.backgroundColor = theme.bg;
  el.style.setProperty('--theme-title-color', theme.titleColor);
  el.style.setProperty('--theme-sub-color', theme.subColor);
  el.style.setProperty('--theme-card-bg', theme.cardBg);
  el.style.setProperty('--theme-card-border', theme.cardBorder);
  el.style.setProperty('--theme-desc-color', theme.descColor);
  el.style.setProperty('--theme-icon-bg', theme.iconBg);
  el.style.setProperty('--theme-icon-color', theme.iconColor);
}

interface ScrollThemeProviderProps {
  children: ReactNode;
}

export function ScrollThemeProvider({ children }: ScrollThemeProviderProps) {
  const backdropRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    const backdrop = backdropRef.current;
    if (!backdrop) return;

    // Set the initial (dark) state immediately — no flash on load
    applyVars(backdrop, DARK);

    // The FeaturesSection must render a <div data-theme-trigger="light"> element
    // and a <div data-theme-trigger="dark"> for the exit.
    const lightTrigger = document.querySelector<HTMLElement>(
      '[data-theme-trigger="light"]',
    );
    const darkTrigger = document.querySelector<HTMLElement>(
      '[data-theme-trigger="dark"]',
    );

    if (!lightTrigger || !darkTrigger) return;

    // Optional — CTA section also goes orange on entry
    const ctaLightTrigger = document.querySelector<HTMLElement>(
      '[data-theme-trigger="cta-light"]',
    );

    const ctx = gsap.context(() => {
      // ── Enter light — Features (dark → orange) ────────────────────────
      gsap.timeline({
        scrollTrigger: {
          trigger: lightTrigger,
          start: 'top 30%',
          end: 'top 20%',
          scrub: 0.4,
        },
      }).fromTo(
        backdrop,
        {
          backgroundColor: DARK.bg,
          '--theme-title-color': DARK.titleColor,
          '--theme-sub-color': DARK.subColor,
          '--theme-card-bg': DARK.cardBg,
          '--theme-card-border': DARK.cardBorder,
          '--theme-desc-color': DARK.descColor,
          '--theme-icon-bg': DARK.iconBg,
          '--theme-icon-color': DARK.iconColor,
        },
        {
          backgroundColor: LIGHT.bg,
          '--theme-title-color': LIGHT.titleColor,
          '--theme-sub-color': LIGHT.subColor,
          '--theme-card-bg': LIGHT.cardBg,
          '--theme-card-border': LIGHT.cardBorder,
          '--theme-desc-color': LIGHT.descColor,
          '--theme-icon-bg': LIGHT.iconBg,
          '--theme-icon-color': LIGHT.iconColor,
          ease: 'none',
        },
      );

      // ── Exit light — Features (orange → dark) ─────────────────────────
      gsap.timeline({
        scrollTrigger: {
          trigger: darkTrigger,
          start: 'top 40%',
          end: 'top 30%',
          scrub: 0.4,
        },
      }).fromTo(
        backdrop,
        {
          backgroundColor: LIGHT.bg,
          '--theme-title-color': LIGHT.titleColor,
          '--theme-sub-color': LIGHT.subColor,
          '--theme-card-bg': LIGHT.cardBg,
          '--theme-card-border': LIGHT.cardBorder,
          '--theme-desc-color': LIGHT.descColor,
          '--theme-icon-bg': LIGHT.iconBg,
          '--theme-icon-color': LIGHT.iconColor,
        },
        {
          backgroundColor: DARK.bg,
          '--theme-title-color': DARK.titleColor,
          '--theme-sub-color': DARK.subColor,
          '--theme-card-bg': DARK.cardBg,
          '--theme-card-border': DARK.cardBorder,
          '--theme-desc-color': DARK.descColor,
          '--theme-icon-bg': DARK.iconBg,
          '--theme-icon-color': DARK.iconColor,
          ease: 'none',
        },
      );

      // ── Enter light — CTA (dark → orange) ────────────────────────────
      if (ctaLightTrigger) {
        gsap.timeline({
          scrollTrigger: {
            trigger: ctaLightTrigger,
            start: 'top 65%',
            end: 'top 30%',
            scrub: 0.4,
          },
        }).fromTo(
          backdrop,
          {
            backgroundColor: DARK.bg,
            '--theme-title-color': DARK.titleColor,
            '--theme-sub-color': DARK.subColor,
            '--theme-card-bg': DARK.cardBg,
            '--theme-card-border': DARK.cardBorder,
            '--theme-desc-color': DARK.descColor,
            '--theme-icon-bg': DARK.iconBg,
            '--theme-icon-color': DARK.iconColor,
          },
          {
            backgroundColor: LIGHT.bg,
            '--theme-title-color': LIGHT.titleColor,
            '--theme-sub-color': LIGHT.subColor,
            '--theme-card-bg': LIGHT.cardBg,
            '--theme-card-border': LIGHT.cardBorder,
            '--theme-desc-color': LIGHT.descColor,
            '--theme-icon-bg': LIGHT.iconBg,
            '--theme-icon-color': LIGHT.iconColor,
            ease: 'none',
          },
        );
      }
    });

    return () => ctx.revert();
  }, []);

  return (
    <>
      {/*
       * Single fixed backdrop.
       * – starts at #0D0D0D (same as body bg-primary-bg) so there is
       *   zero flash even before JS hydrates.
       * – CSS variables cascade into all child sections via this element.
       */}
      <div
        ref={backdropRef}
        aria-hidden="true"
        style={{ backgroundColor: '#0D0D0D' }}
        className="pointer-events-none fixed inset-0 -z-10 will-change-[background-color]"
      />
      {children}
    </>
  );
}
