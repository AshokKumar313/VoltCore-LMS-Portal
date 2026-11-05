/**
 * ========================================================================================
 * VoltCore Apex Academia - Enterprise Progressive Web App (PWA) Service Worker
 * Anna University / MIT Campus Standards (Department of Electronics Engineering)
 * ----------------------------------------------------------------------------------------
 * Platform Lead / Architect: Ashok Kumar A
 * Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
 * Version: v4.4.0-Enterprise-PWA
 * 
 * Caching Strategy:
 *   - CacheFirst for Static Assets (/_astro/*, fonts, images, stylesheets)
 *   - NetworkFirst with Cache Fallback for Curriculum Pages & Flashcards
 *   - Offline Synthetic Responses for Disconnected API Endpoints
 * ========================================================================================
 */

const CACHE_NAME = 'voltcore-apex-v4.4.0';

// Core Application Shell Pre-Cache Manifest
const PRECACHE_ASSETS = [
  '/',
  '/attendance',
  '/autograder',
  '/careers',
  '/collaboration',
  '/enterprise-admin',
  '/exam-center',
  '/flash-firmware',
  '/flashcards',
  '/fleet',
  '/gate-ece',
  '/hardware-hil',
  '/nptel',
  '/nptel-player',
  '/profile',
  '/research',
  '/settings',
  '/simulation',
  '/smart-lab',
  '/teacher',
  '/telemetry',
  '/virtual-bench',
  '/manifest.json',
  '/favicon.svg'
];

// Service Worker Install Event - Pre-cache Essential App Shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[VoltCore PWA]: Pre-caching static curriculum assets and offline app shell...');
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Service Worker Activate Event - Purge Obsolete Caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log(`[VoltCore PWA]: Deleting legacy cache store: ${name}`);
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Service Worker Fetch Event - Advanced Hybrid Caching Router
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Ignore non-GET requests (e.g. POST to attendance gateway)
  if (request.method !== 'GET') {
    return;
  }

  // Strategy A: CacheFirst for Static Assets (/_astro/*, fonts, SVG)
  if (
    url.pathname.startsWith('/_astro/') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.woff2') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('fonts.googleapis.com')
  ) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // Strategy B: NetworkFirst with Cache Fallback for HTML Page Routes
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // Offline Fallback: Serve cached page if available, else root shell
          return caches.match(request).then((cachedPage) => {
            if (cachedPage) {
              return cachedPage;
            }
            return caches.match('/');
          });
        })
    );
    return;
  }

  // Strategy C: Network-First for API calls with Synthetic Offline JSON Fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            status: 'offline_spooled',
            message: 'Device is offline. Local LittleFS / IndexedDB spooling is managing telemetry.',
            timestamp: new Date().toISOString()
          }),
          {
            headers: { 'Content-Type': 'application/json' },
            status: 200
          }
        );
      })
    );
    return;
  }

  // Default Fallback
  event.respondWith(
    caches.match(request).then((response) => response || fetch(request))
  );
});

// Service Worker Message Channel - Trigger Instant Update
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
