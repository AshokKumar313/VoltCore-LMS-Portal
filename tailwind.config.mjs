/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#020813',
          900: '#041026',
          850: '#061735',
          800: '#0a214d',
          700: '#113575',
        },
        emerald: {
          accent: '#00F0B5',
          300: '#34d399',
          400: '#00F0B5',
          500: '#00b884',
          600: '#008f65',
          700: '#00693E',
          800: '#004c2c',
        },
        cyber: {
          cyan: '#00D8F6',
          purple: '#9D4EDD',
          amber: '#FFB703',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        academic: ['Computer Modern', 'Latin Modern Roman', 'STIX Two Text', 'Georgia', 'serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.45)',
        'emerald-glow': '0 0 30px rgba(0, 240, 181, 0.22)',
        'cyber-glow': '0 0 25px rgba(0, 216, 246, 0.25)',
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle at 50% 0%, rgba(0, 240, 181, 0.12) 0%, rgba(2, 8, 19, 0) 70%)',
      }
    },
  },
  plugins: [],
};

