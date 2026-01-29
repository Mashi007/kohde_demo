import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

// Middleware para logging de requests
app.use((req, res, next) => {
  console.log(`${req.method} ${req.path}`);
  next();
});

// Servir archivos estáticos desde el directorio dist
const distPath = path.join(__dirname, 'dist');
console.log('Directorio dist:', distPath);
console.log('¿Existe dist?', existsSync(distPath));

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
  
  if (ext && staticExtensions.includes(ext.toLowerCase())) {
    // Si es un archivo estático que no existe, devolver 404
    console.log(`Archivo estático no encontrado: ${req.path}`);
    return res.status(404).send('Archivo no encontrado');
  }
  
  // Para todas las demás rutas (incluyendo /items, /items?, /inventario, etc.), servir index.html
  const indexPath = path.join(distPath, 'index.html');
  console.log(`Sirviendo index.html para ruta: ${req.path}`);
  
  if (!existsSync(indexPath)) {
    console.error(`ERROR: index.html no existe en ${indexPath}`);
    return res.status(500).send('Error: index.html no encontrado');
  }
  
  res.sendFile(indexPath, (err) => {
    if (err) {
      console.error('Error al servir index.html:', err);
      console.error('Ruta solicitada:', req.path);
      console.error('Directorio dist:', distPath);
      res.status(500).send('Error interno del servidor');
    } else {
      console.log(`✓ index.html servido correctamente para ${req.path}`);
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✓ Servidor corriendo en puerto ${PORT}`);
  console.log(`✓ Sirviendo archivos estáticos desde: ${distPath}`);
  console.log(`✓ Listo para recibir requests`);
});
