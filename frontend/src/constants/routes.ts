/**
 * Application route constants.
 * Single source of truth for all internal navigation paths.
 */
export const ROUTES = {
  HOME: '/',
  EXPLORE: '/explore',
  SONG: (id: string) => `/song/${id}` as const,
  TRANSLATE: '/translate',
  LIBRARY: '/library',
  ABOUT: '/about',
} as const;

/** Navigation items rendered in the navbar. */
export const NAV_ITEMS = [
  { label: 'Home', href: ROUTES.HOME },
  { label: 'Explore', href: ROUTES.EXPLORE },
  { label: 'Translate', href: ROUTES.TRANSLATE },
  { label: 'Library', href: ROUTES.LIBRARY },
  { label: 'About', href: ROUTES.ABOUT },
] as const;
