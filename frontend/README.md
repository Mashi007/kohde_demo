# Frontend ERP Restaurantes

Frontend React para el sistema ERP de restaurantes.

## 🚀 Instalación

```bash
cd frontend
npm install
```

## 🛠️ Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

## 📦 Build para Producción

```bash
npm run build
```

Los archivos se generarán en la carpeta `dist/`

## 🔧 Configuración

Crea un archivo `.env` con:

```
VITE_API_URL=http://localhost:5000/api
```

Para producción, usa la URL de tu backend en Render:
```
VITE_API_URL=https://tu-backend.onrender.com/api
```

## 📁 Estructura

```
frontend/
├── src/
│   ├── components/     # Componentes reutilizables
│   ├── pages/         # Páginas principales
│   ├── config/        # Configuración (API, etc.)
│   └── App.jsx        # Componente principal
├── public/            # Archivos estáticos
└── package.json       # Dependencias
```

## 🎨 Tecnologías

- **React 18** - Framework UI
- **React Router** - Navegación
- **TanStack Query** - Gestión de estado del servidor
- **Axios** - Cliente HTTP
- **Tailwind CSS** - Estilos
- **Lucide React** - Iconos
- **React Hot Toast** - Notificaciones
- **Vite** - Build tool

## 📱 Páginas Implementadas

- ✅ Dashboard
- ✅ Clientes
- ✅ Facturas
- 🚧 Tickets
- 🚧 Inventario
- 🚧 Items
- 🚧 Recetas
- 🚧 Programación
- 🚧 Proveedores
- 🚧 Pedidos

## 🔗 Conexión con Backend

El frontend se conecta al backend a través de la variable `VITE_API_URL`.

En desarrollo, Vite hace proxy de `/api` a `http://localhost:5000`.
