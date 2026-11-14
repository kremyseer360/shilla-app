const CACHE = 'shilla-v15-1';
const SHELL = ['./', './index.html', './manifest.json', './icons/icon-192.png', './icons/icon-512.png', './assets/music/manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(async c => {
      await c.addAll(SHELL).catch(() => {});
      try {
        const res = await fetch('./assets/music/manifest.json', { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          const tracks = Array.isArray(data.tracks) ? data.tracks : [];
          for (const t of tracks) {
            if (t && t.file) {
              const url = './assets/music/' + String(t.file).replace(/^\/+/, '').split('/').map(encodeURIComponent).join('/');
              await c.add(url).catch(() => {});
            }
          }
        }
      } catch (err) {}
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  e.respondWith(
    fetch(req).then(res => {
      if (res && res.status === 200) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
      }
      return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('./index.html')))
  );
});
