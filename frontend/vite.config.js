import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, existsSync, writeFileSync, mkdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

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
          // Crear directorio dist si no existe
          const distDir = join(__dirname, 'dist')
          if (!existsSync(distDir)) {
            mkdirSync(distDir, { recursive: true })
          }
          
          if (existsSync(src)) {
            copyFileSync(src, dest)
            console.log('✓ _redirects copiado al build')
          } else {
            // Intentar con path relativo desde el directorio del proyecto
            const altSrc = join(process.cwd(), 'frontend', 'public', '_redirects')
            if (existsSync(altSrc)) {
              copyFileSync(altSrc, dest)
              console.log('✓ _redirects copiado al build (path alternativo)')
            } else {
              // Crear archivo _redirects si no existe
              writeFileSync(dest, '/*    /index.html   200')
              console.log('✓ Archivo _redirects creado en build')
            }
          }
        } catch (error) {
          console.warn('⚠ No se pudo copiar _redirects:', error.message)
          // Intentar crear el archivo como fallback
          try {
            const distDir = join(__dirname, 'dist')
            if (!existsSync(distDir)) {
              mkdirSync(distDir, { recursive: true })
            }
            writeFileSync(dest, '/*    /index.html   200')
            console.log('✓ Archivo _redirects creado como fallback')
          } catch (e) {
            console.warn('⚠ No se pudo crear _redirects:', e.message)
          }
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
