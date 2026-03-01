import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  site: 'https://faith-driven-life.netlify.app', // Set your Netlify URL or use env in Netlify dashboard
  integrations: [mdx(), sitemap(), tailwind()]
});