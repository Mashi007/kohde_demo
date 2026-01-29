import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// ============================================================================
// CONFIGURACIÓN BÁSICA
// ============================================================================

app.disable('x-powered-by');
app.set('trust proxy', 1);

// ============================================================================
// DETECCIÓN DE DIRECTORIO DIST
// ============================================================================

let distPath = path.join(__dirname, 'dist');

if (!existsSync(distPath)) {
  const possiblePaths = [
    path.join(process.cwd(), 'dist'),
    path.join(process.cwd(), 'frontend', 'dist'),
    path.resolve(__dirname, 'dist'),
    path.resolve(process.cwd(), 'dist'),
  ];
  
  for (const possiblePath of possiblePaths) {
    if (existsSync(possiblePath)) {
      distPath = possiblePath;
      console.log(`[INFO] Encontrado dist en: ${distPath}`);
      break;
    }
  }
}

if (!existsSync(distPath)) {
  console.error('[ERROR CRÍTICO] No se pudo encontrar el directorio dist');
  console.error('[ERROR CRÍTICO] Directorio actual:', process.cwd());
  console.error('[ERROR CRÍTICO] __dirname:', __dirname);
  process.exit(1);
}

const indexPath = path.join(distPath, 'index.html');
if (!existsSync(indexPath)) {
  console.error('[ERROR CRÍTICO] index.html no existe en:', indexPath);
  process.exit(1);
}

console.log('=== SERVIDOR EXPRESS INICIANDO ===');
console.log('Directorio dist:', distPath);
console.log('index.html:', indexPath);
console.log('¿Existe index.html?', existsSync(indexPath));

// ============================================================================
// MIDDLEWARE DE SEGURIDAD
// ============================================================================

app.use((req, res, next) => {
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  next();
});

// ============================================================================
// HEALTH CHECK (ANTES DEL HANDLER SPA)
// ============================================================================

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// ============================================================================
// FAVICON
// ============================================================================

app.get('/favicon.ico', (req, res) => {
  res.status(204).end();
});

// ============================================================================
// SERVIR ARCHIVOS ESTÁTICOS
// ============================================================================

// IMPORTANTE: fallthrough: true permite que continúe al siguiente middleware si el archivo no existe
app.use(express.static(distPath, {
  maxAge: '1d',
  etag: true,
  lastModified: true,
  fallthrough: true, // CRÍTICO: continuar si el archivo no existe
  index: false, // No servir index.html automáticamente
}));

// ============================================================================
// HANDLER SPA - DEBE IR DESPUÉS DE express.static
// ============================================================================

// Capturar TODAS las rutas GET que no sean archivos estáticos
app.get('*', (req, res) => {
  const url = req.url;
  // Limpiar el path: remover query string y trailing slash
  let pathOnly = url.split('?')[0];
  // Remover trailing slash excepto para root
  if (pathOnly !== '/' && pathOnly.endsWith('/')) {
    pathOnly = pathOnly.slice(0, -1);
  }
  const ext = path.extname(pathOnly).toLowerCase();
  
  // Extensiones de archivos estáticos
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.map'];
  
  // Si tiene extensión de archivo estático y llegamos aquí, no existe
  if (ext && staticExtensions.includes(ext)) {
    if (ext === '.ico') {
      return res.status(204).end();
    }
    return res.status(404).json({ error: 'Archivo no encontrado' });
  }
  
  // Para todas las demás rutas (sin extensión o rutas SPA), servir index.html
  console.log(`[SPA] Sirviendo index.html para: ${pathOnly}${req.url.includes('?') ? ' (con query string)' : ''}`);
  
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  
  const absoluteIndexPath = path.resolve(indexPath);
  res.sendFile(absoluteIndexPath, (err) => {
    if (err) {
      if (!res.headersSent) {
        console.error(`[ERROR] Error al servir index.html para ${pathOnly}:`, err.message);
        res.status(500).json({ error: 'Error interno del servidor' });
      }
    } else {
      console.log(`[✓] index.html servido para: ${pathOnly}`);
    }
  });
});

// ============================================================================
// MANEJO DE ERRORES
// ============================================================================

app.use((err, req, res, next) => {
  console.error('[ERROR]', err);
  res.status(err.status || 500).json({ error: 'Error interno del servidor' });
});

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const server = app.listen(PORT, HOST, () => {
  console.log(`=== SERVIDOR EXPRESS INICIADO ===`);
  console.log(`✓ Puerto: ${PORT}`);
  console.log(`✓ Host: ${HOST}`);
  console.log(`✓ Directorio dist: ${distPath}`);
  console.log(`✓ Listo para recibir requests`);
});

// Cierre graceful
const gracefulShutdown = (signal) => {
  console.log(`\n[${signal}] Cerrando servidor...`);
  server.close(() => {
    console.log('✓ Servidor cerrado');
    process.exit(0);
  });
  setTimeout(() => {
    console.error('⚠ Forzando cierre...');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

process.on('uncaughtException', (err) => {
  console.error('[FATAL]', err);
  gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason) => {
  console.error('[FATAL] Promesa rechazada:', reason);
});
