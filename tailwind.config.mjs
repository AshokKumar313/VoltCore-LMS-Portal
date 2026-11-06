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
        },
        olive: {
          950: '#12180C',
          900: '#1C2612',
          800: '#2A3A1C',
          700: '#3D5228',
          600: '#547037',
          500: '#6E9248',
          400: '#8AB45C',
          300: '#ABCF80',
          accent: '#84A950',
        },
        mustard: {
          950: '#211704',
          900: '#362507',
          800: '#52390B',
          700: '#785311',
          600: '#A37117',
          500: '#CF8F1E',
          400: '#E5A93C',
          300: '#F5C56B',
          accent: '#FFC83B',
        },
        course: {
          emerald: '#00F0B5',
          amber: '#F59E0B',
          cyan: '#06B6D4',
          indigo: '#6366F1',
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
        'olive-glow': '0 0 30px rgba(110, 146, 72, 0.32)',
        'mustard-glow': '0 0 30px rgba(229, 169, 60, 0.32)',
        'jewel-glow': '0 0 35px rgba(207, 143, 30, 0.25)',
        'course-emerald-glow': '0 0 25px rgba(0, 240, 181, 0.35)',
        'course-amber-glow': '0 0 25px rgba(245, 158, 11, 0.35)',
        'course-cyan-glow': '0 0 25px rgba(6, 182, 212, 0.35)',
        'course-indigo-glow': '0 0 25px rgba(99, 102, 241, 0.35)',
        'course-emerald-inner': 'inset 0 0 15px rgba(0, 240, 181, 0.20)',
        'course-amber-inner': 'inset 0 0 15px rgba(245, 158, 11, 0.20)',
        'course-cyan-inner': 'inset 0 0 15px rgba(6, 182, 212, 0.20)',
        'course-indigo-inner': 'inset 0 0 15px rgba(99, 102, 241, 0.20)',
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle at 50% 0%, rgba(0, 240, 181, 0.12) 0%, rgba(2, 8, 19, 0) 70%)',
      }
    },
  },
  plugins: [],
};

