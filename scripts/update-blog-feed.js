#!/usr/bin/env node
/**
 * Fetches Blogger feed and writes blog-feed.json to repo root.
 * Run: node scripts/update-blog-feed.js
 * Used by GitHub Actions to keep the static feed updated (no CORS on the site).
 */
const fs = require('fs');
const path = require('path');
const https = require('https');

const FEED_URL = 'https://awfgsa.blogspot.com/feeds/posts/default?alt=json&max-results=50';
const OUT_FILE = path.join(__dirname, '..', 'blog-feed.json');

function fetch(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers: { Accept: 'application/json' }, timeout: 15000 }, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
  });
}

fetch(FEED_URL)
  .then((data) => {
    fs.writeFileSync(OUT_FILE, JSON.stringify(data), 'utf8');
    const count = (data && data.feed && data.feed.entry && data.feed.entry.length) || 0;
    console.log('Wrote', OUT_FILE, '–', count, 'entries');
  })
  .catch((err) => {
    console.error('Error:', err.message);
    process.exit(1);
  });
