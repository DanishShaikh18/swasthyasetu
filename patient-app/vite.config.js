import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /\/api\/v1\/(patients\/me|content\/first-aid|content\/daily-tip)/,
            handler: 'CacheFirst',
            options: { cacheName: 'api-cache', expiration: { maxAgeSeconds: 86400 } }
          }
        ]
      },
      manifest: {
        name: 'SwasthyaSetu — स्वास्थ्य सेतु',
        short_name: 'SwasthyaSetu',
        theme_color: '#1A6B4A',
        background_color: '#F7F5F0',
        display: 'standalone',
        orientation: 'portrait',
        lang: 'hi',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ],
  server: { port: 5173 }
})
