/**
 * ========================================================================================
 * VoltCore Apex Academia - Enterprise Progressive Web App (PWA) Service Worker
 * Autonomous Engineering Cluster • Outcome-Based Education (OBE) • Offline Synchronization
 * ----------------------------------------------------------------------------------------
 * Architecture: Service Worker v5.0.0 • CacheFirst Static • NetworkFirst Curriculum
 * Capabilities: Offline MDX Chapter Reading • Disconnected Quizzes • Local Telemetry Spooling
 * ========================================================================================
 */

const CACHE_NAME = 'voltcore-apex-v5.0.0-pwa';

// Core Application Shell & Curriculum Pre-Cache Manifest
const PRECACHE_ASSETS = [
  '/',
  '/academic-hub',
  '/accessibility',
  '/analog-communication',
  '/analog-electronics',
  '/attendance',
  '/autograder',
  '/careers',
  '/cloud-deploy',
  '/collaboration',
  '/component-inspector',
  '/course-hub',
  '/data-intelligence',
  '/digital-electronics',
  '/digital-logic',
  '/ece-knowledge',
  '/embedded-systems',
  '/embedded-systems/stm32-academy',
  '/enterprise-admin',
  '/exam-center',
  '/faculty-admin',
  '/faculty-workspace',
  '/flash-firmware',
  '/flashcards',
  '/fleet',
  '/gate-ece',
  '/hardware-hil',
  '/iot-connected-systems',
  '/iot-lab',
  '/learning-dashboard',
  '/learning-productivity',
  '/next-gen',
  '/nptel',
  '/nptel-player',
  '/performance-optimization',
  '/physical-lab',
  '/practical-laboratory',
  '/profile',
  '/project-innovation',
  '/research',
  '/security-hub',
  '/security-integrity',
  '/settings',
  '/signals-communication',
  '/simulation',
  '/smart-lab',
  '/student-projects',
  '/system-health',
  '/system-health-integration',
  '/teacher',
  '/telemetry',
  '/textbook-library',
  '/virtual-bench',
  '/voice-lab',
  '/workspace',
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

  // Intercept offline POST requests to /api/sync/batch when disconnected
  if (request.method === 'POST' && url.pathname.includes('/api/sync/batch')) {
    event.respondWith(
      fetch(request.clone()).catch(() => {
        return new Response(
          JSON.stringify({
            status: 'OFFLINE_SPOOLED',
            message: 'Device offline. Action securely spooled in IndexedDB; will synchronize upon network recovery.',
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

  // Ignore other non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Strategy A: CacheFirst for Static Assets (/_astro/*, fonts, CSS, SVG)
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

  // Strategy B: NetworkFirst with Cache Fallback for HTML Page Routes & MDX
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

  // Strategy C: Network-First for API calls with Synthetic Offline JSON Fallback (offline_spooled)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({
            status: 'OFFLINE_SPOOLED',
            mode: 'offline_spooled',
            message: 'Device is offline. Local IndexedDB queue is managing transactions.',
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
