const express = require('express');
const path = require('path');
const app = express();

// Servir archivos estáticos desde el directorio dist
app.use(express.static(path.join(__dirname, 'dist')));

// Manejar todas las rutas - redirigir a index.html para SPA routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});
