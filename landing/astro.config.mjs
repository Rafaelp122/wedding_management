// @ts-check
import process from 'node:process';
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: process.env.SITE_URL || 'https://simaceito.rafaelpdev.com.br',
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()]
  }
});
