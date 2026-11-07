import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

/**
 * Vite plugin to safeguard @astrojs/react:opts hook against unfiltered invocations in Vite 5.
 * @astrojs/react v7 uses Rolldown/Vite 8 object filters ({ filter: { id: ... }, handler() }),
 * which in Vite 5 causes the load handler to fire on every requested file (including index.astro),
 * injecting the raw options literal and throwing a syntax error at line 24.
 */
function fixReactOptsPlugin() {
  return {
    name: 'voltcore:fix-react-opts',
    configResolved(config) {
      const reactOpts = config.plugins.find((p) => p.name === '@astrojs/react:opts');
      if (reactOpts) {
        const origLoad = typeof reactOpts.load === 'object' ? reactOpts.load.handler : reactOpts.load;
        if (typeof origLoad === 'function') {
          reactOpts.load = function (id) {
            if (id !== '\0astro:react:opts') return null;
            return origLoad.call(this, id);
          };
        }
        const origResolve = typeof reactOpts.resolveId === 'object' ? reactOpts.resolveId.handler : reactOpts.resolveId;
        if (typeof origResolve === 'function') {
          reactOpts.resolveId = function (id) {
            if (id !== 'astro:react:opts') return null;
            return origResolve.call(this, id);
          };
        }
      }
    },
  };
}

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
  vite: {
    plugins: [fixReactOptsPlugin()],
  },
});
