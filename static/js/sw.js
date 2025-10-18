// static/sw.js
const CACHE_NAME = 'bluecollar-resume-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/css/responsive.css',
    '/static/js/main.js',
    '/static/js/voice-input.js',
    '/static/js/chatbot.js',
    '/static/images/logo.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});