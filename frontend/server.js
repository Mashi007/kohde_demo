import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readdirSync, statSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// ============================================================================
// CONFIGURACIÓN DE SEGURIDAD Y RENDIMIENTO
// ============================================================================

// Deshabilitar header X-Powered-By por seguridad
app.disable('x-powered-by');

// Trust proxy (necesario para Render y otros proxies)
app.set('trust proxy', 1);

// ============================================================================
// DETECCIÓN DE DIRECTORIO DIST
// ============================================================================

let distPath = path.join(__dirname, 'dist');

// Si no existe, intentar otras rutas posibles
if (!existsSync(distPath)) {
  const possiblePaths = [
    path.join(process.cwd(), 'dist'),           // Si estamos en frontend/ y cwd es frontend/
    path.join(process.cwd(), 'frontend', 'dist'), // Si estamos en raíz y cwd es raíz
    path.resolve(__dirname, 'dist'),            // Ruta absoluta desde __dirname
    path.resolve(process.cwd(), 'dist'),        // Ruta absoluta desde cwd
  ];
  
  for (const possiblePath of possiblePaths) {
    if (existsSync(possiblePath)) {
      distPath = possiblePath;
      console.log(`[INFO] Encontrado dist en: ${distPath}`);
      break;
    }
  }
}

// Validar que dist existe antes de continuar
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
console.log('Directorio actual (__dirname):', __dirname);
console.log('Directorio dist:', distPath);
console.log('¿Existe dist?', existsSync(distPath));

// Verificar archivos en dist
if (existsSync(distPath)) {
  try {
    const files = readdirSync(distPath);
    console.log(`Archivos en dist (${files.length} total):`, files.slice(0, 10));
    console.log('¿Existe index.html?', existsSync(indexPath));
  } catch (e) {
    console.error('Error leyendo dist:', e.message);
  }
}

// ============================================================================
// MIDDLEWARE DE SEGURIDAD
// ============================================================================

// Headers de seguridad para todas las respuestas
app.use((req, res, next) => {
  // Prevenir clickjacking
  res.setHeader('X-Frame-Options', 'DENY');
  // Prevenir MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');
  // XSS Protection
  res.setHeader('X-XSS-Protection', '1; mode=block');
  // Referrer Policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  // Permissions Policy (antes Feature-Policy)
  res.setHeader('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  next();
});

// ============================================================================
// MIDDLEWARE DE LOGGING MEJORADO
// ============================================================================

app.use((req, res, next) => {
  const start = Date.now();
  const url = req.url;
  const pathOnly = url.split('?')[0];
  
  // Logging solo en desarrollo o para rutas importantes
  const isProduction = process.env.NODE_ENV === 'production';
  const shouldLog = !isProduction || pathOnly.includes('/api') || pathOnly === '/';
  
  if (shouldLog) {
    console.log(`[${new Date().toISOString()}] ${req.method} ${pathOnly}${url !== pathOnly ? '?' + url.split('?')[1] : ''} - IP: ${req.ip}`);
  }
  
  // Medir tiempo de respuesta
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (shouldLog && duration > 1000) {
      console.warn(`[SLOW] ${req.method} ${pathOnly} tomó ${duration}ms`);
    }
  });
  
  next();
});

// ============================================================================
// MANEJO DE FAVICON
// ============================================================================

app.get('/favicon.ico', (req, res) => {
  // El favicon está embebido en el HTML como data URI, pero algunos navegadores lo solicitan
  res.status(204).end(); // No Content
});

// ============================================================================
// SERVIR ARCHIVOS ESTÁTICOS CON CACHING OPTIMIZADO
// ============================================================================

// Configuración de caching por tipo de archivo
const staticOptions = {
  maxAge: '1d',
  etag: true, // Habilitar ETags para mejor caching
  lastModified: true,
  setHeaders: (res, filePath) => {
    const ext = path.extname(filePath).toLowerCase();
    
    // Archivos de aplicación (JS, CSS) - cache corto con revalidación
    if (['.js', '.css'].includes(ext)) {
      res.setHeader('Cache-Control', 'public, max-age=86400, must-revalidate');
    }
    // Assets estáticos (imágenes, fuentes) - cache largo
    else if (['.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot'].includes(ext)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    }
    // Otros archivos
    else {
      res.setHeader('Cache-Control', 'public, max-age=86400');
    }
  },
  fallthrough: true // Continuar al siguiente middleware si el archivo no existe
};

app.use(express.static(distPath, staticOptions));

// ============================================================================
// RUTA SPA - SERVIR INDEX.HTML PARA TODAS LAS RUTAS
// ============================================================================

app.get('*', (req, res, next) => {
  const url = req.url;
  const pathOnly = url.split('?')[0];
  const ext = path.extname(pathOnly);
  
  // Lista de extensiones de archivos estáticos
  const staticExtensions = ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.json', '.xml', '.map'];
  
  // Si tiene extensión de archivo estático, ya debería haber sido servido por express.static
  // Si llegamos aquí con una extensión estática, significa que no existe
  if (ext && staticExtensions.includes(ext.toLowerCase())) {
    // Para .ico, retornar 204 (No Content) en lugar de 404
    if (ext.toLowerCase() === '.ico') {
      return res.status(204).end();
    }
    // Para otros archivos estáticos, retornar 404
    return res.status(404).json({ error: 'Archivo no encontrado' });
  }
  
  // Validar que index.html existe (ya validado al inicio, pero verificamos de nuevo)
  if (!existsSync(indexPath)) {
    console.error(`[ERROR CRÍTICO] index.html no existe en ${indexPath}`);
    return res.status(500).json({ error: 'Error interno del servidor: index.html no encontrado' });
  }
  
  // Servir index.html con headers apropiados para SPA
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  // No cachear index.html para asegurar que siempre se obtenga la versión más reciente
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  
  // Usar sendFile con la ruta absoluta
  const absoluteIndexPath = path.resolve(indexPath);
  res.sendFile(absoluteIndexPath, (err) => {
    if (err) {
      // Solo loggear errores si la respuesta no se ha enviado
      if (!res.headersSent) {
        console.error(`[ERROR] Error al servir index.html:`, err.message);
        console.error(`[ERROR] Stack:`, err.stack);
        console.error(`[ERROR] Ruta solicitada: ${pathOnly}`);
        console.error(`[ERROR] indexPath: ${absoluteIndexPath}`);
        res.status(500).json({ error: 'Error interno del servidor' });
      } else {
        // Si los headers ya se enviaron, solo loggear el error
        console.error(`[ERROR] Error después de enviar headers para: ${pathOnly}`, err.message);
      }
    }
  });
});

// ============================================================================
// MANEJO DE ERRORES GLOBAL
// ============================================================================

// Middleware de manejo de errores (debe ir al final, después de todas las rutas)
app.use((err, req, res, next) => {
  console.error('[ERROR] Error no manejado:', err);
  console.error('[ERROR] Stack:', err.stack);
  
  // No exponer detalles del error en producción
  const isDevelopment = process.env.NODE_ENV !== 'production';
  const message = isDevelopment ? err.message : 'Error interno del servidor';
  
  res.status(err.status || 500).json({
    error: message,
    ...(isDevelopment && { stack: err.stack })
  });
});

// Manejar rutas no encontradas (solo para API, las rutas SPA ya están manejadas arriba)
app.use((req, res) => {
  // Si llegamos aquí y no es una ruta SPA, es un 404 real
  const ext = path.extname(req.path).toLowerCase();
  if (ext && ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg'].includes(ext)) {
    res.status(404).json({ error: 'Archivo no encontrado' });
  } else {
    // Para rutas sin extensión, ya deberían haber sido manejadas por el handler SPA
    // Si llegamos aquí, algo salió mal
    res.status(404).json({ error: 'Ruta no encontrada' });
  }
});

// ============================================================================
// INICIALIZACIÓN DEL SERVIDOR
// ============================================================================

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

const server = app.listen(PORT, HOST, () => {
  console.log(`=== SERVIDOR EXPRESS INICIADO ===`);
  console.log(`✓ Puerto: ${PORT}`);
  console.log(`✓ Host: ${HOST}`);
  console.log(`✓ Directorio dist: ${distPath}`);
  console.log(`✓ Entorno: ${process.env.NODE_ENV || 'development'}`);
  console.log(`✓ Ruta de trabajo: ${process.cwd()}`);
  console.log(`✓ Listo para recibir requests`);
});

// ============================================================================
// MANEJO DE CIERRE GRACEFUL
// ============================================================================

// Manejar señales de terminación para cierre graceful
const gracefulShutdown = (signal) => {
  console.log(`\n[${signal}] Recibida señal de terminación. Cerrando servidor...`);
  
  server.close(() => {
    console.log('✓ Servidor cerrado correctamente');
    process.exit(0);
  });
  
  // Forzar cierre después de 10 segundos
  setTimeout(() => {
    console.error('⚠ Forzando cierre del servidor...');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// ============================================================================
// MANEJO DE ERRORES NO CAPTURADOS
// ============================================================================

process.on('uncaughtException', (err) => {
  console.error('[FATAL] Excepción no capturada:', err);
  console.error('[FATAL] Stack:', err.stack);
  // En producción, podrías querer enviar una notificación aquí
  gracefulShutdown('uncaughtException');
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[FATAL] Promesa rechazada no manejada:', reason);
  console.error('[FATAL] Promise:', promise);
  // En producción, podrías querer enviar una notificación aquí
  // No terminamos el proceso aquí, solo loggeamos
});

// ============================================================================
// HEALTH CHECK (opcional, útil para Render)
// ============================================================================

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});
