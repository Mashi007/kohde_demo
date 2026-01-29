import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, existsSync } from 'fs'
import { join } from 'path'

export default defineConfig({
  plugins: [
    react(),
    // Plugin para asegurar que _redirects se copie al build
    {
      name: 'copy-redirects',
      closeBundle() {
        const src = join(__dirname, 'public', '_redirects')
        const dest = join(__dirname, 'dist', '_redirects')
        try {
          if (existsSync(src)) {
            copyFileSync(src, dest)
            console.log('✓ _redirects copiado al build')
          }
        } catch (error) {
          console.warn('⚠ No se pudo copiar _redirects:', error.message)
        }
      },
    },
  ],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    // Copiar archivo _redirects al build para Render
    copyPublicDir: true,
  },
  publicDir: 'public',
})
