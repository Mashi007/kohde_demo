# 📦 Módulo de Logística - Estructura Completa

## ✅ Estructura del Módulo Logística

El módulo de Logística ahora agrupa todos los componentes relacionados con la gestión de inventario, compras y facturación:

```
modules/logistica/
├── __init__.py
├── items.py              ✅ Gestión de items/productos
├── inventario.py         ✅ Control de inventario
├── facturas.py           ✅ Procesamiento de facturas con OCR
├── pedidos.py            ✅ Gestión de pedidos de compra
└── requerimientos.py     ✅ Requerimientos de materiales
```

---

## 📋 Componentes del Módulo

### 1. **Items** (`modules/logistica/items.py`)
- Gestión del catálogo de productos/insumos
- Categorización de items
- Control de códigos únicos
- Gestión de costos unitarios

### 2. **Inventario** (`modules/logistica/inventario.py`)
- Control de stock
- Alertas de stock bajo
- Verificación de disponibilidad
- Movimientos de inventario

### 3. **Facturas** (`modules/logistica/facturas.py`)
- Procesamiento de facturas con OCR (Google Cloud Vision)
- Ingreso desde imágenes/PDF
- Aprobación de facturas
- Actualización automática de inventario

### 4. **Pedidos** (`modules/logistica/pedidos.py`)
- Creación de pedidos de compra
- Generación automática de pedidos
- Envío de pedidos a proveedores
- Notificaciones por WhatsApp y Email

### 5. **Requerimientos** (`modules/logistica/requerimientos.py`)
- Gestión de requerimientos de materiales
- Procesamiento de requerimientos
- Entrega de items

---

## 🎯 Endpoints Disponibles

### Items (`/api/logistica/items`)
- `GET /api/logistica/items` - Listar items
- `POST /api/logistica/items` - Crear item
- `GET /api/logistica/items/:id` - Obtener item
- `PUT /api/logistica/items/:id` - Actualizar item
- `PUT /api/logistica/items/:id/costo` - Actualizar costo

### Inventario (`/api/logistica/inventario`)
- `GET /api/logistica/inventario` - Listar inventario
- `GET /api/logistica/inventario/:item_id` - Obtener inventario de item
- `GET /api/logistica/inventario/stock-bajo` - Items con stock bajo
- `POST /api/logistica/inventario/:item_id/verificar` - Verificar disponibilidad
- `POST /api/logistica/inventario/:item_id/ajustar` - Ajustar inventario

### Facturas (`/api/logistica/facturas`)
- `GET /api/logistica/facturas` - Listar facturas
- `POST /api/logistica/facturas/ingresar-imagen` - Procesar factura con OCR
- `GET /api/logistica/facturas/:id` - Obtener factura
- `POST /api/logistica/facturas/:id/aprobar` - Aprobar factura

### Pedidos (`/api/logistica/pedidos`)
- `GET /api/logistica/pedidos` - Listar pedidos
- `POST /api/logistica/pedidos` - Crear pedido
- `POST /api/logistica/pedidos/automatico` - Generar pedidos automáticos
- `POST /api/logistica/pedidos/:id/enviar` - Enviar pedido

### Requerimientos (`/api/logistica/requerimientos`)
- `GET /api/logistica/requerimientos` - Listar requerimientos
- `POST /api/logistica/requerimientos` - Crear requerimiento
- `POST /api/logistica/requerimientos/:id/procesar` - Procesar requerimiento

---

## 🔄 Flujo de Datos

```
┌─────────────────┐
│   Facturas      │
│   (OCR)         │
└────────┬────────┘
         │ Aprobación
         ▼
┌─────────────────┐
│   Inventario    │
│   (Actualizado) │
└────────┬────────┘
         │ Stock bajo
         ▼
┌─────────────────┐
│   Requerimientos│
│   (Generados)   │
└────────┬────────┘
         │ Agrupación
         ▼
┌─────────────────┐
│   Pedidos       │
│   (Automáticos) │
└─────────────────┘
```

---

## 📊 Integración con Otros Módulos

### CRM (Proveedores)
- Los pedidos se relacionan con proveedores del módulo CRM
- Las facturas se relacionan con proveedores del módulo CRM
- Notificaciones se envían a proveedores via WhatsApp/Email

### Planificación
- Los requerimientos pueden generarse desde la planificación de menús
- Los items se usan en recetas

---

## ✅ Estado Actual

### Backend
- ✅ Todos los servicios en `modules/logistica/`
- ✅ Todas las rutas en `routes/logistica_routes.py`
- ✅ Endpoints funcionando correctamente
- ✅ Integración con OCR (Google Cloud Vision)
- ✅ Notificaciones integradas

### Frontend
- ✅ `Facturas.jsx` - Usa `/api/logistica/facturas`
- ✅ `Pedidos.jsx` - Usa `/api/logistica/pedidos`
- ✅ `Items.jsx` - Usa `/api/logistica/items`
- ✅ `Inventario.jsx` - Usa `/api/logistica/inventario`
- ✅ `Dashboard.jsx` - Usa `/api/logistica/facturas` y `/api/logistica/inventario`

---

## 📝 Notas Importantes

1. **Facturas**: Procesamiento automático con OCR, creación automática de proveedores e items si no existen.

2. **Pedidos Automáticos**: Se generan agrupados por proveedor basándose en requerimientos y stock bajo.

3. **Inventario**: Se actualiza automáticamente al aprobar facturas.

4. **Notificaciones**: Los pedidos envían notificaciones automáticas a proveedores.

---

**Última actualización**: 2026-01-29
