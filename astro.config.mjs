import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  server: {
    port: 4321,
    host: true,
  },
  integrations: [
    tailwind({
      applyBaseStyles: true,
      configFile: './tailwind.config.mjs',
    }),
    react(),
    mdx(),
  ],
});
