/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        dental: {
          bg: '#0F172A',
          surface: '#1E293B',
          surfaceHighlight: '#334155',
          primary: '#0D9488',
          primaryGlow: 'rgba(13, 148, 136, 0.4)',
          accent: '#06B6D4',
          textMain: '#F8FAFC',
          textMuted: '#94A3B8',
        },
        status: {
          caries: '#EF4444',
          lesion: '#F97316',
          implant: '#3B82F6',
          healthy: '#22C55E',
          boneLoss: '#EAB308',
        },
      },
      animation: {
        'scan-line': 'scan-line 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
      },
      keyframes: {
        'scan-line': {
          '0%, 100%': { transform: 'translateY(-100%)' },
          '50%': { transform: 'translateY(100%)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
