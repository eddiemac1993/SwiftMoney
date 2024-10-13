self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open('static-cache').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/css/styles.css',
        '/static/js/main.js',
        '/static/icons/android-chrome-192x192.png',
        '/static/icons/android-chrome-512x512.png',
      ]).catch(function(error) {
        console.error('Failed to cache resources:', error);
        // Log which resources failed to cache
      });
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).catch(() => caches.match('/offline.html'));
    })
  );
});