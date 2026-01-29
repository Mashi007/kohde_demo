import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Servir archivos estáticos desde el directorio dist
const distPath = path.join(__dirname, 'dist');

console.log('=== SERVIDOR EXPRESS INICIANDO ===');
console.log('Directorio actual (__dirname):', __dirname);
console.log('Directorio dist:', distPath);
console.log('¿Existe dist?', existsSync(distPath));

if (existsSync(distPath)) {
  try {
    const files = readdirSync(distPath);
    console.log(`Archivos en dist (${files.length} total):`, files.slice(0, 10));
    console.log('¿Existe index.html?', existsSync(path.join(distPath, 'index.html')));
  } catch (e) {
    console.error('Error leyendo dist:', e.message);
  }
}

// Middleware para logging de requests
app.use((req, res, next) => {
  const url = req.url;
  const pathOnly = url.split('?')[0];
  console.log(`[${new Date().toISOString()}] ${req.method} ${pathOnly}${url !== pathOnly ? '?' + url.split('?')[1] : ''}`);
  next();
});

// Servir archivos estáticos (JS, CSS, imágenes, etc.)
app.use(express.static(distPath, {
  maxAge: '1d',
  etag: false,
  fallthrough: true // Continuar al siguiente middleware si el archivo no existe
}));

// Manejar todas las demás rutas - servir index.html para SPA routing
// IMPORTANTE: Este handler debe estar DESPUÉS de express.static para capturar rutas no encontradas
app.get('*', (req, res, next) => {
  const url = req.url;
  const pathOnly = url.split('?')[0];
  const ext = path.extname(pathOnly);
  
  // Lista de extensiones de archivos estáticos
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.map'];
  
  console.log(`[SPA Handler] ${req.method} ${pathOnly}${url !== pathOnly ? '?' + url.split('?')[1] : ''}`);
  console.log(`[SPA Handler] Extensión: ${ext || 'none'}`);
  
  // Si tiene extensión de archivo estático, ya debería haber sido servido por express.static
  // Si llegamos aquí con una extensión estática, significa que no existe
  if (ext && staticExtensions.includes(ext.toLowerCase())) {
    console.log(`[404] Archivo estático no encontrado: ${pathOnly}`);
    return res.status(404).send('Archivo no encontrado');
  }
  
  // Para todas las demás rutas (incluyendo /items, /items?, /inventario, etc.), servir index.html
  const indexPath = path.join(distPath, 'index.html');
  
  if (!existsSync(indexPath)) {
    console.error(`[ERROR CRÍTICO] index.html no existe en ${indexPath}`);
    console.error(`[ERROR CRÍTICO] Directorio dist: ${distPath}`);
    console.error(`[ERROR CRÍTICO] Directorio actual: ${process.cwd()}`);
    try {
      const files = readdirSync(distPath);
      console.error(`[ERROR CRÍTICO] Archivos disponibles en dist:`, files.slice(0, 20));
    } catch (e) {
      console.error(`[ERROR CRÍTICO] No se pudo leer directorio:`, e.message);
    }
    return res.status(500).send('Error: index.html no encontrado');
  }
  
  // Servir index.html con headers apropiados para SPA
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  
  console.log(`[✓] Sirviendo index.html para ruta: ${pathOnly}`);
  
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error(`[ERROR] Error al servir index.html:`, err.message);
      console.error(`[ERROR] Stack:`, err.stack);
      console.error(`[ERROR] Ruta solicitada: ${pathOnly}`);
      if (!res.headersSent) {
        res.status(500).send('Error interno del servidor');
      }
    } else {
      console.log(`[✓] index.html servido exitosamente para: ${pathOnly}`);
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`=== SERVIDOR EXPRESS INICIADO ===`);
  console.log(`✓ Puerto: ${PORT}`);
  console.log(`✓ Directorio: ${distPath}`);
  console.log(`✓ Listo para recibir requests`);
  console.log(`✓ Ruta de trabajo: ${process.cwd()}`);
  console.log(`✓ Variables de entorno PORT: ${process.env.PORT}`);
});

// Manejar errores no capturados
process.on('uncaughtException', (err) => {
  console.error('ERROR NO CAPTURADO:', err);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('PROMESA RECHAZADA NO MANEJADA:', reason);
});
