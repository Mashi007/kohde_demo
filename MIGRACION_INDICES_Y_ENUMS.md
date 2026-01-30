# Migración: Simplificar Enums y Agregar Índices

**Fecha:** 30 de Enero, 2026  
**Migración:** `39df3de8b2c0_simplificar_enums_y_agregar_indices`  
**Objetivo:** Simplificar enums a strings y agregar índices para mejorar consultas

---

## 📋 Resumen de la Migración

Esta migración realiza dos mejoras importantes:

1. **Simplifica enums a strings** - Cambia `estadopedido` de enum a VARCHAR simple
2. **Agrega índices** - Mejora el rendimiento de consultas frecuentes

---

## ✅ Cambios Realizados

### 1. Simplificación de Enum

**Tabla:** `pedidos_compra`  
**Columna:** `estado`

**Antes:**
- Tipo: `enum estadopedido` (PostgreSQL enum)
- Valores almacenados como nombres en mayúsculas
- Conversiones complejas entre Python y PostgreSQL

**Después:**
- Tipo: `VARCHAR(20)`
- Valores: `'borrador'`, `'enviado'`, `'recibido'`, `'cancelado'` (minúsculas)
- CheckConstraint para validación
- Más simple y práctico

**Beneficios:**
- ✅ Consultas SQL más simples
- ✅ Sin conversiones complejas
- ✅ Compatible con el AI Chat
- ✅ Fácil de usar en queries

### 2. Índices Agregados

Se agregaron **25 índices** en tablas críticas para mejorar el rendimiento:

#### 📦 Pedidos de Compra (4 índices):
- `ix_pedidos_compra_estado` - Consultas por estado
- `ix_pedidos_compra_fecha_pedido` - Ordenamiento por fecha
- `ix_pedidos_compra_proveedor_id` - JOINs con proveedores
- `ix_pedidos_compra_estado_fecha` - Consultas combinadas

#### 💰 Facturas (4 índices):
- `ix_facturas_estado` - Filtrado por estado
- `ix_facturas_fecha_recepcion` - Ordenamiento por fecha
- `ix_facturas_proveedor_id` - JOINs con proveedores
- `ix_facturas_estado_fecha` - Consultas combinadas

#### 📊 Inventario (2 índices):
- `ix_inventario_item_id` - JOINs con items
- `ix_inventario_ubicacion` - Filtrado por ubicación

#### 📋 Items (4 índices):
- `ix_items_codigo` - Búsqueda por código
- `ix_items_activo` - Filtrado por activo
- `ix_items_categoria` - Filtrado por categoría
- `ix_items_proveedor_autorizado` - JOINs con proveedores

#### 👥 Proveedores (2 índices):
- `ix_proveedores_nombre` - Búsqueda por nombre
- `ix_proveedores_activo` - Filtrado por activo

#### 📋 Recetas (2 índices):
- `ix_recetas_activa` - Filtrado por activa
- `ix_recetas_tipo` - Filtrado por tipo

#### 📅 Programación (3 índices):
- `ix_programacion_menu_fecha` - Filtrado por fecha
- `ix_programacion_menu_ubicacion` - Filtrado por ubicación
- `ix_programacion_menu_fecha_ubicacion` - Consultas combinadas

#### 🍽️ Charolas (2 índices):
- `ix_charolas_fecha_servicio` - Filtrado por fecha
- `ix_charolas_ubicacion` - Filtrado por ubicación

#### 📊 Mermas (2 índices):
- `ix_mermas_fecha_merma` - Filtrado por fecha
- `ix_mermas_item_id` - JOINs con items

#### 💬 Chat (4 índices):
- `ix_conversaciones_activa` - Filtrado por activa
- `ix_conversaciones_fecha_actualizacion` - Ordenamiento
- `ix_mensajes_conversacion_id` - JOINs con conversaciones
- `ix_mensajes_fecha_envio` - Ordenamiento por fecha

---

## 🚀 Cómo Aplicar la Migración

### Opción 1: Aplicar Manualmente en Render

1. **Conectar a la base de datos de Render:**
   ```bash
   # Obtener DATABASE_URL desde Render Dashboard
   psql $DATABASE_URL
   ```

2. **Ejecutar la migración:**
   ```bash
   alembic upgrade head
   ```

### Opción 2: Aplicar Automáticamente en el Inicio

Agregar al `startCommand` en Render:

```bash
alembic upgrade head && gunicorn app:app --bind 0.0.0.0:$PORT
```

### Opción 3: Script de Migración

Crear un script `scripts/aplicar_migracion.py`:

```python
from app import create_app
from alembic.config import Config
from alembic import command

app = create_app()
with app.app_context():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("✅ Migración aplicada exitosamente")
```

---

## 📊 Mejoras de Rendimiento Esperadas

### Consultas que se Benefician:

1. **Pedidos por estado:**
   ```sql
   SELECT * FROM pedidos_compra WHERE estado = 'borrador'
   ```
   **Mejora:** 10-100x más rápido con índice

2. **Facturas pendientes:**
   ```sql
   SELECT * FROM facturas WHERE estado = 'pendiente' ORDER BY fecha_recepcion DESC
   ```
   **Mejora:** 5-50x más rápido con índices combinados

3. **Items con inventario bajo:**
   ```sql
   SELECT i.* FROM items i 
   JOIN inventario inv ON i.id = inv.item_id 
   WHERE inv.cantidad_actual < inv.cantidad_minima AND i.activo = true
   ```
   **Mejora:** 3-20x más rápido con índices en item_id y activo

4. **Charolas por fecha:**
   ```sql
   SELECT * FROM charolas WHERE fecha_servicio >= CURRENT_DATE - INTERVAL '7 days'
   ```
   **Mejora:** 5-30x más rápido con índice en fecha_servicio

---

## ⚠️ Consideraciones

### Antes de Aplicar:

1. **Backup:** Hacer backup de la base de datos antes de aplicar
2. **Mantenimiento:** La migración puede tomar tiempo si hay muchos registros
3. **Downtime:** Considerar aplicar durante mantenimiento programado

### Después de Aplicar:

1. **Verificar índices:**
   ```sql
   SELECT indexname, tablename FROM pg_indexes 
   WHERE schemaname = 'public' 
   ORDER BY tablename, indexname;
   ```

2. **Verificar constraint:**
   ```sql
   SELECT conname, contype FROM pg_constraint 
   WHERE conname = 'check_estado_pedido_valido';
   ```

3. **Probar consultas:** Verificar que las consultas frecuentes sean más rápidas

---

## 🔄 Rollback (Si es Necesario)

Si necesitas revertir la migración:

```bash
alembic downgrade -1
```

**Nota:** El rollback eliminará los índices pero mantendrá el VARCHAR (no revierte a enum por simplicidad).

---

## ✅ Verificación Post-Migración

Después de aplicar la migración, verifica:

1. ✅ Los índices fueron creados correctamente
2. ✅ El CheckConstraint está activo
3. ✅ Las consultas funcionan correctamente
4. ✅ El rendimiento mejoró en consultas frecuentes

### Consultas de Verificación:

```sql
-- Verificar índices creados
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'ix_%';

-- Verificar constraint
SELECT conname FROM pg_constraint 
WHERE conname = 'check_estado_pedido_valido';

-- Probar consulta optimizada
EXPLAIN ANALYZE 
SELECT * FROM pedidos_compra 
WHERE estado = 'borrador' 
ORDER BY fecha_pedido DESC LIMIT 10;
```

---

## 📝 Notas

- Los índices ocupan espacio adicional en la base de datos (~5-10% más)
- Los índices mejoran SELECT pero pueden ralentizar INSERT/UPDATE ligeramente
- Los índices se actualizan automáticamente cuando cambian los datos
- El CheckConstraint asegura integridad de datos a nivel de BD

---

**Migración creada:** 30 de Enero, 2026  
**Estado:** Lista para aplicar  
**Tiempo estimado:** 1-5 minutos (depende del tamaño de la BD)
