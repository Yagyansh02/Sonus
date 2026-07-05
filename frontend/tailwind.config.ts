import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary-bg': '#0D0D0D',
        'secondary-bg': '#181818',
        surface: '#222222',
        accent: '#F15C43',
        'hover-accent': '#FF7B61',
        'primary-text': '#F7F2E8',
        'secondary-text': '#CFC8BE',
        muted: '#8D8D8D',
        card: '#1B1B1B',
        border: 'rgba(255,255,255,0.08)',
      },
      fontFamily: {
        heading: ['var(--font-cormorant)', 'Georgia', 'Times New Roman', 'serif'],
        body: ['var(--font-inter)', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        card: '16px',
        pill: '9999px',
        input: '12px',
      },
      spacing: {
        'section-desktop': '120px',
        'section-tablet': '80px',
        'section-mobile': '48px',
      },
      maxWidth: {
        container: '1280px',
      },
      boxShadow: {
        card: '0 4px 24px rgba(0,0,0,0.2)',
        'card-hover': '0 12px 40px rgba(0,0,0,0.4)',
        'accent-glow': '0 4px 16px rgba(241,92,67,0.25)',
        'accent-glow-hover': '0 8px 24px rgba(241,92,67,0.35)',
      },
      animation: {
        'bounce-slow': 'bounce 1.4s infinite',
      },
    },
  },
  plugins: [],
};

export default config;
