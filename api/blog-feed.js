/**
 * Vercel serverless function: proxy Blogger JSON feed so the site can load posts
 * without CORS. Called by blogs.html as same-origin /api/blog-feed.
 */
const BLOGGER_FEED = 'https://awfgsa.blogspot.com/feeds/posts/default?alt=json&max-results=50';

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');
  res.setHeader('Access-Control-Allow-Origin', '*');
  try {
    const response = await fetch(BLOGGER_FEED, {
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(15000),
    });
    if (!response.ok) {
      res.status(502).json({ error: 'Blog feed unavailable' });
      return;
    }
    const data = await response.json();
    res.status(200).json(data);
  } catch (err) {
    console.error('blog-feed proxy error:', err.message);
    res.status(502).json({ error: 'Could not load blog feed' });
  }
};
