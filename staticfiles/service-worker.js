// Install event: caching static resources
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('static-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/css/styles.css',
        '/static/js/main.js',
        '/static/icons/android-chrome-192x192.png',
        '/static/icons/android-chrome-512x512.png',
        '/offline.html' // Add an offline fallback page
      ]).catch(function(error) {
        console.error('Failed to cache resources:', error);
      });
    })
  );
});

// Fetch event: serving cached content when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).catch(() => caches.match('/offline.html'));
    })
  );
});

// Sync event: background synchronization (example)
self.addEventListener('sync', function(event) {
  if (event.tag === 'sync-tag') {
    event.waitUntil(
      // Add your sync logic here
      syncFunction().catch(function(error) {
        console.error('Background sync failed:', error);
      })
    );
  }
});

// Push notifications
self.addEventListener('push', function(event) {
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/icons/android-chrome-192x192.png',
    badge: '/static/icons/android-chrome-192x192.png'
  };
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// This is the "Offline page" service worker

importScripts('https://storage.googleapis.com/workbox-cdn/releases/5.1.2/workbox-sw.js');

const CACHE = "pwabuilder-page";

// TODO: replace the following with the correct offline fallback page i.e.: const offlineFallbackPage = "offline.html";
const offlineFallbackPage = "ToDo-replace-this-name.html";

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener('install', async (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.add(offlineFallbackPage))
  );
});

if (workbox.navigationPreload.isSupported()) {
  workbox.navigationPreload.enable();
}

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const preloadResp = await event.preloadResponse;

        if (preloadResp) {
          return preloadResp;
        }

        const networkResp = await fetch(event.request);
        return networkResp;
      } catch (error) {

        const cache = await caches.open(CACHE);
        const cachedResp = await cache.match(offlineFallbackPage);
        return cachedResp;
      }
    })());
  }
});