'use client';

import { Toaster } from 'react-hot-toast';

/**
 * Pre-configured toast notification provider with dark theme styling.
 */
export function ToastProvider() {
  return (
    <Toaster
      position="bottom-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1B1B1B',
          color: '#F7F2E8',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: '12px',
          fontSize: '14px',
          fontFamily: 'var(--font-inter)',
        },
        success: {
          iconTheme: {
            primary: '#F15C43',
            secondary: '#F7F2E8',
          },
        },
        error: {
          iconTheme: {
            primary: '#ef4444',
            secondary: '#F7F2E8',
          },
        },
      }}
    />
  );
}
