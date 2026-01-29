# 📋 Reorganización del Módulo Logística

## ✅ Cambios Realizados

### Estructura Nueva del Módulo Logística

El módulo Logística ahora agrupa cinco componentes principales:

```
modules/logistica/
├── __init__.py
├── items.py              # ✅ Ya estaba en Logística
├── inventario.py         # ✅ Ya estaba en Logística
├── requerimientos.py     # ✅ Ya estaba en Logística
├── facturas.py           # ✅ Movido desde modules/contabilidad/
└── pedidos.py            # ✅ Movido desde modules/compras/
```

---

## 📦 Archivos Movidos

### 1. **Facturas**
- **Desde**: `modules/contabilidad/ingreso_facturas.py`
- **Hacia**: `modules/logistica/facturas.py`
- **Rutas**: Movidas de `/api/contabilidad/facturas` a `/api/logistica/facturas`

### 2. **Pedidos**
- **Desde**: `modules/compras/pedidos.py`
- **Hacia**: `modules/logistica/pedidos.py`
- **Rutas**: Movidas de `/api/compras/pedidos` a `/api/logistica/pedidos`

---

## 🔄 Cambios en Rutas

### Backend (`routes/logistica_routes.py`)

**Agregadas rutas de Facturas:**
- `GET /api/logistica/facturas` - Listar facturas
- `POST /api/logistica/facturas/ingresar-imagen` - Subir factura con OCR
- `GET /api/logistica/facturas/:id` - Obtener factura
- `POST /api/logistica/facturas/:id/aprobar` - Aprobar factura

**Agregadas rutas de Pedidos:**
- `GET /api/logistica/pedidos` - Listar pedidos
- `POST /api/logistica/pedidos` - Crear pedido
- `POST /api/logistica/pedidos/automatico` - Generar pedido automático
- `POST /api/logistica/pedidos/:id/enviar` - Enviar pedido

**Rutas existentes (ya estaban):**
- Items: `GET /api/logistica/items`, `POST /api/logistica/items`, etc.
- Inventario: `GET /api/logistica/inventario`, `GET /api/logistica/inventario/stock-bajo`, etc.
- Requerimientos: `GET /api/logistica/requerimientos`, `POST /api/logistica/requerimientos`, etc.

### Backend (`routes/contabilidad_routes.py`)

**Removidas rutas de Facturas** (ahora en Logística):
- Todas las rutas `/api/contabilidad/facturas` fueron movidas

**Rutas de Plan Contable (permanecen en Contabilidad):**
- `GET /api/contabilidad/cuentas` - Listar cuentas
- `GET /api/contabilidad/cuentas/arbol` - Árbol de cuentas
- `POST /api/contabilidad/cuentas` - Crear cuenta
- `GET /api/contabilidad/cuentas/:id` - Obtener cuenta

### Backend (`routes/compras_routes.py`)

**Removidas rutas de Pedidos** (ahora en Logística):
- Todas las rutas `/api/compras/pedidos` fueron movidas

**Nota**: El módulo de Compras ahora está vacío (solo tiene un endpoint de salud).

---

## 🔧 Actualizaciones de Importaciones

### Backend

**Archivos actualizados:**
1. `routes/logistica_routes.py`
   - ✅ Agregado: `from modules.logistica.facturas import FacturaService`
   - ✅ Agregado: `from modules.logistica.pedidos import PedidoCompraService`

2. `routes/contabilidad_routes.py`
   - ✅ Removido: `from modules.contabilidad.ingreso_facturas import FacturaService`

3. `routes/compras_routes.py`
   - ✅ Removido: `from modules.compras.pedidos import PedidoCompraService`

4. `routes/whatsapp_webhook.py`
   - ✅ Actualizado: `from modules.logistica.facturas import FacturaService`

5. `modules/configuracion/whatsapp.py`
   - ✅ Actualizado: `from modules.logistica.facturas import FacturaService`

6. `modules/planificacion/programacion.py`
   - ✅ Actualizado: `from modules.logistica.pedidos import PedidoCompraService`

### Frontend

**Archivos actualizados:**
1. `frontend/src/pages/Facturas.jsx`
   - ✅ Actualizado: `api.get('/logistica/facturas')` (antes `/contabilidad/facturas`)
   - ✅ Actualizado: `api.post('/logistica/facturas/:id/aprobar')`

2. `frontend/src/pages/Pedidos.jsx`
   - ✅ Actualizado: `api.get('/logistica/pedidos')` (antes `/compras/pedidos`)

3. `frontend/src/components/FacturaUploadForm.jsx`
   - ✅ Actualizado: `api.post('/logistica/facturas/ingresar-imagen')`

4. `frontend/src/pages/Dashboard.jsx`
   - ✅ Actualizado: `api.get('/logistica/facturas?estado=pendiente')`

---

## 📊 Estructura Final del Módulo Logística

### Componentes del Módulo Logística:

1. **Items** (`modules/logistica/items.py`)
   - Catálogo de productos/insumos
   - Gestión de códigos, categorías, unidades
   - Costos unitarios

2. **Inventario** (`modules/logistica/inventario.py`)
   - Control de stock
   - Alertas de stock bajo
   - Verificación de disponibilidad

3. **Requerimientos** (`modules/logistica/requerimientos.py`)
   - Gestión de requerimientos de items
   - Procesamiento y entrega

4. **Facturas** (`modules/logistica/facturas.py`)
   - Ingreso de facturas con OCR
   - Procesamiento automático
   - Aprobación y actualización de inventario

5. **Pedidos** (`modules/logistica/pedidos.py`)
   - Creación de pedidos de compra
   - Generación automática de pedidos
   - Envío a proveedores

---

## 🎯 Endpoints Disponibles

### Logística - Items
- `GET /api/logistica/items` - Listar items
- `POST /api/logistica/items` - Crear item
- `GET /api/logistica/items/:id` - Obtener item
- `PUT /api/logistica/items/:id` - Actualizar item
- `PUT /api/logistica/items/:id/costo` - Actualizar costo

### Logística - Inventario
- `GET /api/logistica/inventario` - Listar inventario
- `GET /api/logistica/inventario/stock-bajo` - Stock bajo
- `POST /api/logistica/inventario/:id/verificar` - Verificar disponibilidad

### Logística - Requerimientos
- `GET /api/logistica/requerimientos` - Listar requerimientos
- `POST /api/logistica/requerimientos` - Crear requerimiento
- `POST /api/logistica/requerimientos/:id/procesar` - Procesar requerimiento

### Logística - Facturas
- `GET /api/logistica/facturas` - Listar facturas
- `POST /api/logistica/facturas/ingresar-imagen` - Subir factura con OCR
- `GET /api/logistica/facturas/:id` - Obtener factura
- `POST /api/logistica/facturas/:id/aprobar` - Aprobar factura

### Logística - Pedidos
- `GET /api/logistica/pedidos` - Listar pedidos
- `POST /api/logistica/pedidos` - Crear pedido
- `POST /api/logistica/pedidos/automatico` - Generar pedido automático
- `POST /api/logistica/pedidos/:id/enviar` - Enviar pedido

---

## ✅ Verificación

### Backend
- ✅ Archivos movidos correctamente
- ✅ Importaciones actualizadas
- ✅ Rutas reorganizadas
- ✅ Servicios funcionando

### Frontend
- ✅ URLs actualizadas a `/api/logistica/facturas` y `/api/logistica/pedidos`
- ✅ Componentes funcionando correctamente

---

## 📝 Notas Importantes

1. **Contabilidad ahora solo tiene Plan Contable**: El módulo de Contabilidad ahora solo maneja cuentas contables. Las facturas están en Logística.

2. **Compras está vacío**: El módulo de Compras ahora solo tiene un endpoint de salud. Los pedidos están en Logística.

3. **Flujo completo en Logística**: Ahora todo el flujo de compras está centralizado:
   - Items → Inventario → Requerimientos → Pedidos → Facturas → Inventario

4. **Compatibilidad**: Las rutas antiguas `/api/contabilidad/facturas` y `/api/compras/pedidos` ya no existen. Todas las referencias fueron actualizadas.

---

**Última actualización**: 2026-01-29
