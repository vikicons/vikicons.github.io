// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://vikicons.vn',
  base: '/', // Giữ nguyên '/' khi sử dụng Custom Domain trỏ thẳng gốc
  vite: {
    plugins: [tailwindcss()]
  }
});