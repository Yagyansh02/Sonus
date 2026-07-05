'use client';

import type { ReactNode } from 'react';
import { QueryProvider } from './query-provider';
import { ToastProvider } from './toast-provider';

/**
 * Composition root for all client-side providers.
 * Wrap the app tree once in the root layout.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      {children}
      <ToastProvider />
    </QueryProvider>
  );
}
