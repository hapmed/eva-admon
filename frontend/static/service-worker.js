// Service worker de la PWA (Admon).
// Estrategia: navegación network-first con respaldo en caché; assets cache-first.
// La API (/api) nunca se cachea.

const CACHE = 'admon-v1';

self.addEventListener('install', (event) => {
	event.waitUntil(
		caches
			.open(CACHE)
			.then((cache) => cache.addAll(['/']).catch(() => undefined))
			.catch(() => undefined)
	);
	self.skipWaiting();
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches
			.keys()
			.then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
			.then(() => self.clients.claim())
	);
});

self.addEventListener('fetch', (event) => {
	const request = event.request;
	if (request.method !== 'GET') return;

	const url = new URL(request.url);
	if (url.origin !== self.location.origin) return;
	if (url.pathname.startsWith('/api') || url.pathname.startsWith('/healthz')) return;

	if (request.mode === 'navigate') {
		event.respondWith(fetch(request).catch(() => caches.match('/')));
		return;
	}

	event.respondWith(
		caches.match(request).then(
			(cached) =>
				cached ||
				fetch(request)
					.then((response) => {
						if (response.ok) {
							const copy = response.clone();
							caches.open(CACHE).then((cache) => cache.put(request, copy));
						}
						return response;
					})
					.catch(() => cached)
		)
	);
});
