# Mejoras en la Interacción AI-Base de Datos

**Fecha:** 30 de Enero, 2026  
**Objetivo:** Mejorar la capacidad del AI para encontrar información y responder preguntas sobre la base de datos

---

## 🎯 Mejoras Implementadas

### 1. Mapa de Navegación de Información

Se agregó un mapa completo que indica dónde buscar información según el tipo de pregunta:

#### 📊 Información sobre Productos/Items
- **Tabla principal:** `items`
- **Stock actual:** `inventario` (JOIN con items)
- **Historial de costos:** `costo_items` (JOIN con items)
- **Proveedor autorizado:** `items.proveedor_autorizado_id` → `proveedores.id`

#### 💰 Información sobre Compras y Facturación
- **Facturas:** `facturas` (JOIN con proveedores)
- **Items de facturas:** `factura_items` (JOIN facturas + items)
- **Pedidos:** `pedidos_compra` (JOIN con proveedores)
- **Items de pedidos:** `pedido_compra_items` (JOIN pedidos_compra + items)

#### 👥 Información sobre Proveedores
- **Datos del proveedor:** `proveedores`
- **Items que suministra:** `items WHERE proveedor_autorizado_id = X`
- **Facturas del proveedor:** `facturas WHERE proveedor_id = X`
- **Pedidos al proveedor:** `pedidos_compra WHERE proveedor_id = X`

#### 🍽️ Información sobre Servicio y Operaciones
- **Charolas servidas:** `charolas`
- **Items/recetas servidos:** `charola_items` (JOIN charolas + items/recetas)
- **Mermas:** `mermas` (JOIN con items)

#### 📋 Información sobre Planificación
- **Recetas:** `recetas`
- **Ingredientes:** `receta_ingredientes` (JOIN recetas + items)
- **Programación:** `programacion_menu`
- **Items del menú:** `programacion_menu_items` (JOIN programacion_menu + recetas)

---

### 2. Estrategias de Búsqueda

Se agregaron estrategias específicas para diferentes tipos de preguntas:

#### 🔍 Por Tipo de Pregunta:

1. **Cantidades/Números:**
   - Busca en: `inventario` (stock), `charolas` (porciones), `facturas` (totales)
   - Usa: `SUM()`, `COUNT()`, `AVG()`

2. **Fechas:**
   - Busca en: `charolas.fecha_servicio`, `facturas.fecha_recepcion`
   - Usa: `DATE()` para comparar solo la fecha

3. **Producto Específico:**
   - Empieza en: `items` (busca por nombre con `ILIKE`)
   - Luego consulta: `inventario`, `costo_items`, `factura_items`

4. **Proveedor:**
   - Empieza en: `proveedores` (busca por nombre)
   - Luego consulta: `items`, `facturas`, `pedidos_compra`

5. **Charolas/Servicio:**
   - Tabla principal: `charolas`
   - Detalles: `charola_items`
   - Filtra por: `fecha_servicio`, `ubicacion`, `tipo_comida`

---

### 3. Consultas Exploratorias

Se agregaron consultas útiles para cuando el AI no está seguro:

```sql
-- Ver tablas disponibles
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name

-- Ver estructura de una tabla
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'nombre_tabla' 
ORDER BY ordinal_position

-- Ver valores únicos de un campo
SELECT DISTINCT campo FROM tabla LIMIT 20

-- Ver rango de fechas disponibles
SELECT MIN(fecha_campo) as fecha_min, MAX(fecha_campo) as fecha_max 
FROM tabla
```

---

### 4. Estrategia de Respuesta Inteligente

#### ✅ Cuando la Consulta Devuelve Resultados:
- Presenta información clara y estructurada
- Usa números, porcentajes, comparaciones
- Agrupa o resume cuando hay múltiples resultados
- Ejemplo: "Se sirvieron 3 charolas el 29 de enero, con un total de 196 personas"

#### ⚠️ Cuando la Consulta Devuelve 0 Resultados:
- NO dice simplemente "no hay resultados"
- Verifica primero si hay datos en la tabla
- Sugiere fechas alternativas cercanas
- Ofrece hacer una consulta más amplia
- Ejemplo: "No encontré charolas para el 29 de enero. ¿Quieres que busque charolas de fechas cercanas?"

#### ❌ Cuando Hay un Error:
- Explica el error claramente
- Sugiere cómo corregirlo
- Intenta una consulta alternativa más simple

#### 💡 Para Preguntas Complejas:
- Descompone en múltiples consultas si es necesario
- Combina información de varias tablas usando JOINs
- Presenta un resumen completo al final

#### 🎯 Contexto y Relaciones:
- Cuando menciona un item, incluye información relacionada:
  * Stock actual (inventario)
  * Proveedor (items.proveedor_autorizado_id)
  * Costo actual (items.costo_unitario_actual)
- Cuando menciona una charola, incluye:
  * Ubicación y tipo de comida
  * Total de porciones/personas
  * Items/recetas servidos (charola_items)

#### 💬 Sugerencias Proactivas:
- Si pregunta sobre una fecha específica, ofrece información relacionada
- Si pregunta sobre stock bajo, ofrece acciones sugeridas

---

### 5. Manejo Mejorado de Fechas

Se mejoró el manejo de fechas específicas:

```sql
-- Para fecha específica (ej: 29 de enero de 2026)
SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas
FROM charolas 
WHERE DATE(fecha_servicio) = '2026-01-29'
```

**Mejoras:**
- Conversión automática de fechas como "29 de enero" a formato PostgreSQL
- Uso de `DATE()` para comparar solo la fecha (sin hora)
- Si no se menciona el año, usa 2026 (año actual)
- Verificación mejorada cuando no encuentra resultados

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Consulta de Charolas por Fecha
**Usuario:** "el 29 de enero cuantas charolas se sirvieron"

**AI ejecuta:**
```sql
[QUERY_DB]
SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas
FROM charolas 
WHERE DATE(fecha_servicio) = '2026-01-29'
```

**AI responde:** "El 29 de enero se sirvieron 3 charolas con un total de 196 personas. ¿Quieres ver qué items se sirvieron en esas charolas?"

### Ejemplo 2: Consulta de Inventario
**Usuario:** "¿Cuántas libras de pollo tenemos?"

**AI ejecuta:**
```sql
[QUERY_DB]
SELECT i.nombre, inv.cantidad_actual, inv.unidad, inv.ubicacion
FROM inventario inv
JOIN items i ON inv.item_id = i.id
WHERE i.nombre ILIKE '%pollo%' AND i.activo = true
```

**AI responde:** "Tenemos X libras de pollo en la ubicación Y. El stock mínimo es Z libras."

### Ejemplo 3: Cuando No Hay Resultados
**Usuario:** "charolas del 1 de enero"

**AI ejecuta:**
```sql
[QUERY_DB]
SELECT COUNT(*) FROM charolas WHERE DATE(fecha_servicio) = '2026-01-01'
```

**Si no hay resultados:**
**AI responde:** "No encontré charolas para el 1 de enero de 2026. Déjame verificar qué fechas tienen datos disponibles..."

```sql
[QUERY_DB]
SELECT DISTINCT DATE(fecha_servicio) as fecha
FROM charolas 
WHERE fecha_servicio >= '2026-01-01'
ORDER BY fecha DESC
LIMIT 10
```

---

## ✅ Beneficios

1. **Navegación más eficiente:** El AI sabe dónde buscar información
2. **Respuestas más completas:** Incluye información relacionada
3. **Mejor manejo de errores:** Sugiere alternativas cuando no encuentra datos
4. **Consultas más precisas:** Usa el formato correcto de fechas y campos
5. **Experiencia mejorada:** El usuario recibe respuestas útiles incluso cuando no hay datos exactos

---

## 🔄 Próximos Pasos

1. Probar las mejoras en producción
2. Monitorear las consultas del AI para identificar patrones
3. Ajustar el prompt según feedback de usuarios
4. Agregar más ejemplos específicos según casos de uso comunes

---

**Estado:** ✅ Mejoras implementadas y listas para probar
