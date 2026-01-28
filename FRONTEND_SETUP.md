# Guía de Configuración del Frontend

## 🚀 Instalación y Desarrollo

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la carpeta `frontend/`:

```env
VITE_API_URL=http://localhost:5000/api
```

Para producción (cuando el backend esté en Render):
```env
VITE_API_URL=https://tu-backend.onrender.com/api
```

### 3. Ejecutar en desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

---

## 📦 Despliegue en Render

### Opción 1: Static Site (Recomendado)

1. En Render, haz clic en **"New +"**
2. Selecciona **"Static Site"**
3. Conecta tu repositorio
4. Configura:
   - **Name**: `erp-restaurantes-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Environment Variables**:
     ```
     VITE_API_URL=https://tu-backend.onrender.com/api
     ```

### Opción 2: Web Service (con SSR)

Si prefieres usar un servidor Node.js:

1. Crea un servidor simple con Express para servir el build
2. O usa Vite Preview en producción

---

## 🔧 Configuración de CORS

Asegúrate de que tu backend en Render tenga CORS habilitado para el dominio del frontend:

En `app.py` ya está configurado:
```python
CORS(app)  # Permite todas las solicitudes
```

Para producción, puedes restringirlo:
```python
CORS(app, origins=["https://tu-frontend.onrender.com"])
```

---

## 📱 Estructura de Páginas

- **Dashboard** (`/`) - Resumen general
- **Clientes** (`/clientes`) - Gestión de clientes
- **Tickets** (`/tickets`) - Sistema de tickets
- **Facturas** (`/facturas`) - Gestión de facturas
- **Inventario** (`/inventario`) - Control de stock
- **Items** (`/items`) - Catálogo de productos
- **Recetas** (`/recetas`) - Gestión de recetas
- **Programación** (`/programacion`) - Programación de menús
- **Proveedores** (`/proveedores`) - Gestión de proveedores
- **Pedidos** (`/pedidos`) - Pedidos de compra

---

## 🎨 Personalización

### Colores

Los colores principales están en Tailwind:
- **Primario**: `purple-600` (puedes cambiar a tu color)
- **Fondo**: `slate-900` y `slate-800`
- **Texto**: `slate-300` y `white`

### Modificar colores

Edita `tailwind.config.js` o cambia las clases en los componentes.

---

## ✅ Checklist de Despliegue

- [ ] Dependencias instaladas (`npm install`)
- [ ] Archivo `.env` configurado con `VITE_API_URL`
- [ ] Backend funcionando y accesible
- [ ] CORS configurado en backend
- [ ] Build exitoso (`npm run build`)
- [ ] Static Site creado en Render
- [ ] Variables de entorno configuradas en Render
- [ ] Frontend accesible y conectado al backend

---

## 🐛 Solución de Problemas

### Error de CORS
- Verifica que `VITE_API_URL` apunte al backend correcto
- Verifica que CORS esté habilitado en el backend

### Error 404 en rutas
- En Static Site de Render, configura redirects:
  - Crea `frontend/public/_redirects` con: `/* /index.html 200`

### Variables de entorno no funcionan
- Las variables en Vite deben empezar con `VITE_`
- Reinicia el servidor de desarrollo después de cambiar `.env`

---

¡Listo! Tu frontend debería estar funcionando. 🎉
