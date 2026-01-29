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
app.get('*', (req, res) => {
  const url = req.url;
  const pathOnly = url.split('?')[0];
  const ext = path.extname(pathOnly);
  
  // Lista de extensiones de archivos estáticos
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.map'];
  
  console.log(`[SPA Handler] Ruta: ${pathOnly}, ext: ${ext || 'none'}`);
  
  // Si tiene extensión de archivo estático y no existe, retornar 404
  if (ext && staticExtensions.includes(ext.toLowerCase())) {
    console.log(`[404] Archivo estático no encontrado: ${pathOnly}`);
    return res.status(404).send('Archivo no encontrado');
  }
  
  // Para todas las demás rutas (incluyendo /items, /items?, /inventario, etc.), servir index.html
  const indexPath = path.join(distPath, 'index.html');
  
  if (!existsSync(indexPath)) {
    console.error(`[ERROR] index.html no existe en ${indexPath}`);
    console.error(`[ERROR] Directorio dist: ${distPath}`);
    try {
      const files = readdirSync(distPath);
      console.error(`[ERROR] Archivos disponibles:`, files.slice(0, 10));
    } catch (e) {
      console.error(`[ERROR] No se pudo leer directorio:`, e.message);
    }
    return res.status(500).send('Error: index.html no encontrado');
  }
  
  // Servir index.html con headers apropiados para SPA
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache');
  
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error(`[ERROR] Error al servir index.html:`, err.message);
      console.error(`[ERROR] Ruta: ${pathOnly}`);
      if (!res.headersSent) {
        res.status(500).send('Error interno del servidor');
      }
    } else {
      console.log(`[✓] index.html servido para: ${pathOnly}`);
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`=== SERVIDOR EXPRESS INICIADO ===`);
  console.log(`✓ Puerto: ${PORT}`);
  console.log(`✓ Directorio: ${distPath}`);
  console.log(`✓ Listo para recibir requests`);
});
