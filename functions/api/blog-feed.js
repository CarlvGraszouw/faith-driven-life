/**
 * Cloudflare Pages Function: proxy Blogger JSON so blogs.html can fetch same-origin /api/blog-feed (no CORS).
 */
export async function onRequestGet() {
  const BLOGGER_FEED =
    'https://awfgsa.blogspot.com/feeds/posts/default?alt=json&max-results=50';

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(BLOGGER_FEED, {
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      return new Response(JSON.stringify({ error: 'Blog feed unavailable' }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=60',
          'Access-Control-Allow-Origin': '*',
        },
      });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300, must-revalidate',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (err) {
    clearTimeout(timeoutId);
    return new Response(
      JSON.stringify({ error: 'Could not load blog feed' }),
      {
        status: 502,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'public, max-age=60',
          'Access-Control-Allow-Origin': '*',
        },
      }
    );
  }
}
