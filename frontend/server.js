import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Middleware para logging de requests
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}${req.url !== req.path ? ' (query: ' + req.url.split('?')[1] + ')' : ''}`);
  next();
});

// Servir archivos estáticos desde el directorio dist
// __dirname es el directorio donde está server.js (frontend/)
// dist está en frontend/dist, así que la ruta es correcta
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

app.use(express.static(distPath, {
  maxAge: '1d',
  etag: false,
  fallthrough: true // Continuar al siguiente middleware si el archivo no existe
}));

// Manejar todas las rutas - redirigir a index.html para SPA routing
// IMPORTANTE: Esta ruta debe ir después de express.static
app.get('*', (req, res) => {
  // Obtener la ruta sin query string para verificar la extensión
  const pathWithoutQuery = req.path.split('?')[0];
  const ext = path.extname(pathWithoutQuery);
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml'];
  
  console.log(`[SPA Route Handler] Procesando: ${req.path}, ext: ${ext || 'none'}`);
  
  // Si tiene extensión y es un archivo estático, ya fue manejado por express.static
  // Si no existe, express.static con fallthrough:true pasará al siguiente middleware
  if (ext && staticExtensions.includes(ext.toLowerCase())) {
    // Si llegamos aquí, el archivo estático no existe
    console.log(`[404] Archivo estático no encontrado: ${req.path}`);
    return res.status(404).send('Archivo no encontrado');
  }
  
  // Para todas las demás rutas (incluyendo /items, /items?, /inventario, etc.), servir index.html
  const indexPath = path.join(distPath, 'index.html');
  
  console.log(`[SPA] Intentando servir index.html desde: ${indexPath}`);
  
  if (!existsSync(indexPath)) {
    console.error(`[ERROR] index.html no existe en ${indexPath}`);
    console.error(`[ERROR] Directorio dist completo: ${distPath}`);
    try {
      const files = readdirSync(distPath);
      console.error(`[ERROR] Archivos en dist (${files.length} total):`, files.slice(0, 10));
    } catch (e) {
      console.error(`[ERROR] No se pudo leer directorio dist:`, e.message);
    }
    return res.status(500).send('Error: index.html no encontrado');
  }
  
  // Servir index.html con headers apropiados para SPA
  res.setHeader('Content-Type', 'text/html');
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error(`[ERROR] Error al servir index.html para ${req.path}:`, err.message);
      console.error(`[ERROR] Ruta solicitada: ${req.path}`);
      console.error(`[ERROR] Query string:`, req.query);
      console.error(`[ERROR] Directorio dist: ${distPath}`);
      if (!res.headersSent) {
        res.status(500).send('Error interno del servidor');
      }
    } else {
      console.log(`[✓] index.html servido correctamente para ${req.path}`);
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`=== SERVIDOR EXPRESS INICIADO ===`);
  console.log(`✓ Servidor corriendo en puerto ${PORT}`);
  console.log(`✓ Sirviendo archivos estáticos desde: ${distPath}`);
  console.log(`✓ Listo para recibir requests`);
});
