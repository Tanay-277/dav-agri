/* DAV service worker.
 *
 * Scope is deliberately narrow: cache the app shell so the installed app opens
 * instantly and survives a flaky connection, but NEVER cache API or voice
 * traffic. A cached STT/TTS response would replay a stale answer to a farmer as
 * if it were current, which is worse than showing an error.
 *
 * See docs/MOBILE.md.
 */

const CACHE_VERSION = 'dav-shell-v1';
const SHELL_ASSETS = ['/', '/index.html', '/manifest.webmanifest'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Same-origin only. Never touch third-party font requests.
  if (url.origin !== self.location.origin) return;

  // API, voice, docs, health: always straight to the network, never cached.
  if (url.pathname.startsWith('/api/') || url.pathname === '/health' || url.pathname === '/docs') {
    return;
  }

  // Navigations: network first so a deployed update is picked up, falling back
  // to the cached shell when offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put('/index.html', copy));
          return response;
        })
        .catch(() => caches.match('/index.html').then((cached) => cached || caches.match('/')))
    );
    return;
  }

  // Static assets: cache first. Hashed filenames make this safe.
  if (url.pathname.startsWith('/assets/') || url.pathname.startsWith('/icon-')) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            if (response.ok && response.type === 'basic') {
              const copy = response.clone();
              caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
            }
            return response;
          })
      )
    );
  }
});
