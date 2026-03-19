/* Service worker for A Faith Driven Life PWA */
const CACHE_NAME = 'faith-driven-life-v7';
const STATIC_URLS = [
  'index.html',
  'blogs.html',
  'resources.html',
  'community.html',
  'book.html',
  'audio.html',
  'bible.html',
  'comments.html',
  'prayer-requests.html',
  'testimonies.html',
  'verse-pack.html',
  'thanks.html',
  'offline.html',
  'resources/anxiety.html',
  'resources/peace.html',
  'resources/love.html',
  'resources/forgiveness.html',
  'resources/purpose.html',
  'resources/healing.html',
  'logo.png',
  'favicon.svg',
  'manifest.webmanifest'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(STATIC_URLS).catch(function () {});
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (names) {
      return Promise.all(
        names.filter(function (name) { return name !== CACHE_NAME; }).map(function (name) { return caches.delete(name); })
      );
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  if (event.request.method !== 'GET') return;
  var url = new URL(event.request.url);
  if (url.origin !== location.origin) return;

  // For HTML navigations/pages: prefer the network so updates show immediately.
  var accept = event.request.headers && event.request.headers.get ? (event.request.headers.get('accept') || '') : '';
  var isHtml = event.request.mode === 'navigate' || accept.indexOf('text/html') !== -1;

  if (isHtml) {
    event.respondWith(
      fetch(event.request).then(function (res) {
        var clone = res.clone();
        if (res.type === 'basic' && res.status === 200) {
          caches.open(CACHE_NAME).then(function (cache) { cache.put(event.request, clone); });
        }
        return res;
      }).catch(function () {
        return caches.match(event.request).then(function (cached) {
          if (cached) return cached;
          return caches.match('offline.html').then(function (offline) {
            if (offline) return offline;
            return caches.match('index.html');
          }).then(function (c) {
            return c || new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
          });
        });
      })
    );
    return;
  }

  var pathname = url.pathname || '';
  if (pathname === '/blog-feed.json' || pathname.indexOf('blog-feed.json') !== -1) {
    event.respondWith(
      fetch(event.request).then(function (res) {
        var clone = res.clone();
        if (res.type === 'basic' && res.status === 200) {
          caches.open(CACHE_NAME).then(function (cache) { cache.put(event.request, clone); });
        }
        return res;
      }).catch(function () {
        return caches.match(event.request).then(function (cached) { return cached || new Response('{"feed":{"entry":[]}}', { status: 503, headers: { 'Content-Type': 'application/json' } }); });
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(function (cached) {
      if (cached) return cached;
      return fetch(event.request).then(function (res) {
        var clone = res.clone();
        if (res.type === 'basic' && res.status === 200)
          caches.open(CACHE_NAME).then(function (cache) { cache.put(event.request, clone); });
        return res;
      }).catch(function () {
        return caches.match('index.html').then(function (c) { return c || new Response('Offline', { status: 503, statusText: 'Service Unavailable' }); });
      });
    })
  );
});
