/**
 * Design system tokens exposed as JS constants.
 * Used primarily for Framer Motion animations and programmatic style access.
 * CSS custom properties (in globals.css) remain the canonical source for styling.
 */

/* ----------------------- Colors ----------------------------------- */

export const COLORS = {
  primaryBg: '#0D0D0D',
  secondaryBg: '#181818',
  surface: '#222222',
  accent: '#F15C43',
  primaryText: '#F7F2E8',
  secondaryText: '#CFC8BE',
  muted: '#8D8D8D',
  border: 'rgba(255,255,255,0.08)',
  card: '#1B1B1B',
  hoverAccent: '#FF7B61',
} as const;

/* ----------------------- Animation Durations ---------------------- */

export const DURATION = {
  fast: 0.2,
  normal: 0.4,
  slow: 0.6,
  slower: 0.8,
} as const;

/* ----------------------- Easing ----------------------------------- */

export const EASING = {
  smooth: [0.25, 0.1, 0.25, 1] as const,
  decelerate: [0, 0, 0.2, 1] as const,
  accelerate: [0.4, 0, 1, 1] as const,
} as const;

/* ----------------------- Breakpoints ------------------------------ */

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

/* ----------------------- Spacing ---------------------------------- */

export const SECTION_PADDING = {
  desktop: '120px',
  tablet: '80px',
  mobile: '48px',
} as const;

export const MAX_WIDTH = '1280px';

/* ----------------------- Language options for translation ---------- */

export const LANGUAGES = [
  'Hindi',
  'Spanish',
  'French',
  'German',
  'Japanese',
  'Korean',
  'Chinese',
  'Portuguese',
  'Arabic',
  'Russian',
  'Italian',
  'Turkish',
  'Thai',
  'Vietnamese',
  'Swahili',
  'Punjabi',
  'Tamil',
  'Telugu',
  'Bengali',
  'Urdu',
] as const;
