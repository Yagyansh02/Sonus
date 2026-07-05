import type { Metadata } from 'next';
import { Cormorant_Garamond, Inter } from 'next/font/google';
import { AppProviders } from '@/providers/app-providers';
import { Navbar } from '@/components/navigation/navbar';
import { Footer } from '@/components/layout/footer';
import './globals.css';

/* ------------------------------------------------------------------ */
/*  Fonts                                                              */
/* ------------------------------------------------------------------ */

const cormorant = Cormorant_Garamond({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  variable: '--font-cormorant',
  display: 'swap',
});

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
  display: 'swap',
});

/* ------------------------------------------------------------------ */
/*  Metadata                                                           */
/* ------------------------------------------------------------------ */

export const metadata: Metadata = {
  title: {
    default: 'Sonus — Cultural Song Intelligence',
    template: '%s | Sonus',
  },
  description:
    'Transcribe, translate, and interpret songs from any language. AI-powered cultural song analysis for deep musical understanding.',
  keywords: [
    'song analysis',
    'lyrics translation',
    'cultural interpretation',
    'music AI',
    'song meaning',
    'transcription',
  ],
};

/* ------------------------------------------------------------------ */
/*  Root Layout                                                        */
/* ------------------------------------------------------------------ */

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${cormorant.variable} ${inter.variable} antialiased`}
    >
      <body className="min-h-screen flex flex-col bg-[#0D0D0D] text-[#F7F2E8]">
        <AppProviders>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </AppProviders>
      </body>
    </html>
  );
}
