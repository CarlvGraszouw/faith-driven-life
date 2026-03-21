/**
 * Cloudflare Pages Function: proxy Blogger JSON for same-origin /api/blog-feed.
 * CORS: allowlisted production origins + localhost for dev only.
 */
const BLOGGER_FEED =
  'https://awfgsa.blogspot.com/feeds/posts/default?alt=json&max-results=50';

const ALLOWED_ORIGINS = new Set([
  'https://www.afaithdrivenlife.com',
  'https://afaithdrivenlife.com',
  'https://faith-driven-life.pages.dev',
]);

function corsHeaders(request) {
  const origin = request.headers.get('Origin');
  if (!origin) return {};
  if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) {
    return {
      'Access-Control-Allow-Origin': origin,
      Vary: 'Origin',
    };
  }
  if (ALLOWED_ORIGINS.has(origin)) {
    return {
      'Access-Control-Allow-Origin': origin,
      Vary: 'Origin',
    };
  }
  return {};
}

function jsonBody(body, status, cacheControl, request) {
  const c = corsHeaders(request);
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': cacheControl,
      ...c,
    },
  });
}

export async function onRequest(context) {
  const { request } = context;

  if (request.method === 'OPTIONS') {
    const c = corsHeaders(request);
    if (!c['Access-Control-Allow-Origin']) {
      return new Response(null, { status: 204 });
    }
    return new Response(null, {
      status: 204,
      headers: {
        ...c,
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Accept, Content-Type',
        'Access-Control-Max-Age': '86400',
      },
    });
  }

  if (request.method !== 'GET') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders(request),
      },
    });
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(BLOGGER_FEED, {
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return jsonBody(
        JSON.stringify({ error: 'Blog feed unavailable' }),
        502,
        'public, max-age=60',
        request
      );
    }

    const data = await response.json();
    return jsonBody(JSON.stringify(data), 200, 'public, max-age=300, must-revalidate', request);
  } catch (err) {
    clearTimeout(timeoutId);
    return jsonBody(
      JSON.stringify({ error: 'Could not load blog feed' }),
      502,
      'public, max-age=60',
      request
    );
  }
}
