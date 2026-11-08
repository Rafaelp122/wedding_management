// @ts-nocheck
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

const rawSiteUrl = process.env.SITE_URL;
const siteUrl = rawSiteUrl && rawSiteUrl.startsWith('http')
  ? rawSiteUrl
  : 'https://simaceito.rafaelpdev.com.br';

// https://astro.build/config
export default defineConfig({
  site: siteUrl,
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()]
  }
});
