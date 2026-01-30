# Scripts de Inicialización de Datos Mock

Este directorio contiene scripts individuales para inicializar datos de prueba en cada módulo del sistema.

## Scripts Disponibles

### 1. `init_items.py` - Inicializar Items
**Descripción:** Crea 50 items variados (verduras, frutas, carnes, lácteos, productos secos, bebidas, limpieza, panadería).

**Requisitos:**
- Proveedores activos (se crean automáticamente si no existen)
- Labels opcionales (recomendado ejecutar `init_food_labels.py` primero)

**Uso:**
```bash
python scripts/init_items.py
```

**Genera:**
- 50 items variados con códigos únicos
- Relación con proveedores
- Labels asignados según categoría

---

### 2. `init_recetas.py` - Inicializar Recetas
**Descripción:** Crea 12 plantillas de recetas (4 desayunos, 5 almuerzos, 3 cenas) con ingredientes relacionados.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_recetas.py
```

**Genera:**
- 12 recetas completas con ingredientes
- Cálculo automático de calorías, costos y peso total
- Recetas activas listas para usar

---

### 3. `init_facturas.py` - Inicializar Facturas
**Descripción:** Crea 20 facturas variadas con diferentes estados (aprobadas, pendientes, parciales, rechazadas).

**Requisitos:**
- Proveedores activos
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_facturas.py
```

**Genera:**
- 8 facturas aprobadas (para calcular costos promedio)
- 5 facturas pendientes
- 4 facturas parciales
- 3 facturas rechazadas
- Items relacionados con cantidades y precios

---

### 4. `init_inventario.py` - Inicializar Inventario
**Descripción:** Genera inventario realista basado en facturas aprobadas y simula consumos según tipo de item.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)
- Facturas aprobadas (recomendado ejecutar `init_facturas.py` primero)

**Uso:**
```bash
python scripts/init_inventario.py
```

**Genera:**
- Inventario calculado desde facturas aprobadas/parciales
- Consumos simulados realistas según categoría
- Niveles mínimos apropiados por tipo de item
- Alertas de stock bajo/crítico
- Último costo actualizado desde facturas

---

### 5. `init_pedidos.py` - Inicializar Pedidos de Compra
**Descripción:** Crea 10 pedidos de compra variados con diferentes estados (borrador, enviado, recibido, cancelado).

**Requisitos:**
- Proveedores activos (se crean automáticamente con `init_items.py`)
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_pedidos.py
```

**Genera:**
- 10 pedidos de compra con 2-5 items cada uno
- Estados variados: borrador, enviado, recibido, cancelado
- Fechas de pedido y entrega esperada realistas
- Totales calculados automáticamente

---

### 6. `init_pedidos_internos.py` - Inicializar Pedidos Internos
**Descripción:** Crea 10 pedidos internos (transferencia bodega → cocina) con diferentes estados.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_pedidos_internos.py
```

**Genera:**
- 10 pedidos internos con 3-6 items cada uno
- Estados: pendiente, entregado, cancelado
- Responsables de bodega y cocina asignados
- Fechas de pedido y entrega realistas

---

### 7. `init_requerimientos.py` - Inicializar Requerimientos
**Descripción:** Crea 10 requerimientos (salidas de bodega) con diferentes estados.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_requerimientos.py
```

**Genera:**
- 10 requerimientos con 2-4 items cada uno
- Estados: pendiente, entregado, cancelado
- Cantidades solicitadas y entregadas
- Horas de entrega para requerimientos entregados

---

### 8. `init_mermas.py` - Inicializar Mermas
**Descripción:** Crea 10 registros de mermas (pérdidas/desperdicios) variadas.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)

**Uso:**
```bash
python scripts/init_mermas.py
```

**Genera:**
- 10 mermas con diferentes tipos: vencimiento, deterioro, preparación, servicio, otro
- Cantidades y costos calculados
- Motivos y ubicaciones variadas
- Fechas de merma y registro realistas

---

### 9. `init_charolas.py` - Inicializar Charolas
**Descripción:** Crea 10 charolas (bandejas/platos servidos) con items y recetas.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)
- Recetas activas (recomendado ejecutar `init_recetas.py` primero)

**Uso:**
```bash
python scripts/init_charolas.py
```

**Genera:**
- 10 charolas con 2-4 items/recetas cada una
- Tiempos de comida: desayuno, almuerzo, cena
- Cálculo de ventas, costos y ganancias
- Números de charola únicos con formato fecha

---

### 10. `init_costos.py` - Inicializar Costos Estandarizados
**Descripción:** Crea 10 costos estandarizados por item basados en facturas aprobadas.

**Requisitos:**
- Items activos (ejecutar `init_items.py` primero)
- Facturas aprobadas (recomendado ejecutar `init_facturas.py` primero)

**Uso:**
```bash
python scripts/init_costos.py
```

**Genera:**
- 10 costos estandarizados para diferentes items
- Costos promedio calculados
- Variaciones porcentuales y absolutas
- Notas sobre el cálculo y número de facturas usadas

---

## Scripts Maestros

### `init_all_data.py` - Inicializar Todo
Ejecuta todos los scripts en el orden correcto:
1. Labels de alimentos
2. Datos mock completos (proveedores, items, facturas, inventario, recetas)

**Uso:**
```bash
python scripts/init_all_data.py
```

### `init_mock_data.py` - Datos Mock Completos
Script maestro que inicializa todos los módulos en una sola ejecución.

**Uso:**
```bash
python scripts/init_mock_data.py
```

---

## Orden Recomendado de Ejecución

Para inicializar todo desde cero:

```bash
# 1. Labels (opcional pero recomendado)
python scripts/init_food_labels.py

# 2. Items (requiere proveedores, se crean automáticamente)
python scripts/init_items.py

# 3. Facturas (requiere proveedores e items)
python scripts/init_facturas.py

# 4. Inventario (requiere items y facturas recomendadas)
python scripts/init_inventario.py

# 5. Recetas (requiere items)
python scripts/init_recetas.py

# 6. Módulos de Logística (requiere items)
python scripts/init_pedidos.py
python scripts/init_pedidos_internos.py
python scripts/init_requerimientos.py
python scripts/init_mermas.py
python scripts/init_charolas.py
python scripts/init_costos.py
```

O usar el script maestro:

```bash
python scripts/init_all_data.py
```

---

## Características de los Datos Generados

### Items (50 items)
- **Verduras y hortalizas:** 7 items
- **Frutas:** 5 items
- **Carnes:** 7 items
- **Lácteos y huevos:** 6 items
- **Productos secos:** 7 items
- **Condimentos:** 5 items
- **Bebidas:** 6 items
- **Limpieza:** 5 items
- **Panadería:** 3 items

### Recetas (12 plantillas)
- **Desayunos:** 4 recetas
- **Almuerzos:** 5 recetas
- **Cenas:** 3 recetas

### Facturas (20 facturas)
- **Aprobadas:** 8 facturas
- **Pendientes:** 5 facturas
- **Parciales:** 4 facturas
- **Rechazadas:** 3 facturas

### Inventario
- Calculado desde facturas aprobadas
- Consumos simulados realistas
- Niveles mínimos por categoría
- Alertas de stock bajo/crítico

### Módulos de Logística (10 ejemplos cada uno)
- **Pedidos de Compra:** 10 pedidos con estados variados
- **Pedidos Internos:** 10 transferencias bodega → cocina
- **Requerimientos:** 10 salidas de bodega
- **Mermas:** 10 registros de pérdidas/desperdicios
- **Charolas:** 10 bandejas servidas con items/recetas
- **Costos Estandarizados:** 10 costos calculados por item

---

## Notas

- Los scripts son **idempotentes**: pueden ejecutarse múltiples veces sin duplicar datos
- Si un item/receta/factura ya existe, se muestra como "Ya existe" y se omite
- Los scripts verifican dependencias y muestran advertencias si faltan datos previos
- Todos los scripts pueden ejecutarse independientemente si ya existen los datos base
