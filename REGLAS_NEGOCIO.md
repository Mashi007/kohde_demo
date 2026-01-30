# Reglas de Negocio - Sistema de Gestión Restaurante

**Propósito:** Guía para generar datos mock coherentes respetando las reglas del negocio.

---

## 📋 REGLAS GENERALES

### 1. Coherencia Numérica
- Todos los números deben tener sentido lógico
- Las relaciones entre entidades deben ser consistentes
- Los cálculos deben ser correctos (totales, subtotales, IVA, etc.)

### 2. Fechas y Tiempos
- Las fechas deben ser coherentes (fecha_emision < fecha_recepcion)
- Los tiempos de entrega deben ser realistas (1-7 días típicamente)
- Las fechas futuras deben ser razonables

---

## 🍽️ CHAROLAS (Bandejas/Platos Servidos)

### Reglas Principales:
1. **Relación Personas-Charolas:**
   - Para demo simple: **1 charola = 1 persona servida**
   - `personas_servidas` = número de charolas
   - `total_porciones` = personas servidas (para compatibilidad)

2. **Tiempos de Comida:**
   - Valores válidos: `desayuno`, `almuerzo`, `cena`
   - Distribución típica: 30% desayuno, 50% almuerzo, 20% cena
   - Desayuno: 6:00-10:00, Almuerzo: 12:00-15:00, Cena: 18:00-22:00

3. **Ubicaciones:**
   - Valores válidos: `Restaurante_A`, `Restaurante_B`, `Restaurante_C`
   - Distribución típica: 50% Restaurante_A, 30% Restaurante_B, 20% Restaurante_C

4. **Cálculos Financieros:**
   - `total_ventas` = suma de precios de items × cantidad
   - `costo_total` = suma de costos de items × cantidad
   - `ganancia` = `total_ventas` - `costo_total`
   - Margen típico: 30-50% (ganancia / ventas)

5. **Items en Charolas:**
   - Cada charola debe tener al menos 1 item
   - Items típicos: recetas (platos preparados) o items directos
   - Cantidades deben ser realistas (porciones, gramos, unidades)

### Ejemplo Coherente:
```
196 personas servidas = 196 charolas
- 60 charolas desayuno (30%)
- 98 charolas almuerzo (50%)
- 38 charolas cena (20%)
- Distribución: 100 Restaurante_A, 60 Restaurante_B, 36 Restaurante_C
```

---

## 🧾 FACTURAS

### Reglas Principales:
1. **Tipos:**
   - `cliente`: Factura de venta (a clientes)
   - `proveedor`: Factura de compra (de proveedores)

2. **Estados:**
   - `pendiente`: Recién recibida, sin revisar
   - `parcial`: Parcialmente aprobada
   - `aprobada`: Completamente aprobada
   - `rechazada`: Rechazada por algún motivo

3. **Cálculos:**
   - `subtotal` = suma de (cantidad × precio_unitario) de todos los items
   - `iva` = subtotal × 0.16 (16% típico en Ecuador)
   - `total` = subtotal + iva
   - **SIEMPRE:** total = subtotal + iva

4. **Fechas:**
   - `fecha_emision` ≤ `fecha_recepcion`
   - `fecha_recepcion` ≤ fecha actual
   - `fecha_aprobacion` solo si estado = `aprobada` o `parcial`

5. **Items en Facturas:**
   - Cada factura debe tener al menos 1 item
   - `cantidad_facturada` = cantidad en la factura original
   - `cantidad_aprobada` ≤ `cantidad_facturada` (solo si estado = `aprobada` o `parcial`)
   - `subtotal` = cantidad × precio_unitario

### Ejemplo Coherente:
```
Factura de compra:
- subtotal: $1,500.00
- iva (16%): $240.00
- total: $1,740.00
- Items: 3 items (arroz, pollo, verduras)
- Estado: pendiente → aprobada (después de revisión)
```

---

## 📦 PEDIDOS DE COMPRA

### Reglas Principales:
1. **Estados:**
   - `borrador`: En creación, no enviado
   - `enviado`: Enviado al proveedor, esperando respuesta
   - `recibido`: Recibido del proveedor
   - `cancelado`: Cancelado antes de recibir

2. **Flujo de Estados:**
   - borrador → enviado → recibido ✅
   - borrador → cancelado ✅
   - enviado → cancelado ✅
   - ❌ NO: recibido → cancelado (ya recibido)

3. **Fechas:**
   - `fecha_pedido` ≤ `fecha_entrega_esperada`
   - `fecha_entrega_esperada` típicamente 1-7 días después de `fecha_pedido`

4. **Cálculos:**
   - `total` = suma de (cantidad × precio_unitario) de todos los items
   - Cada item debe tener: cantidad, precio_unitario, subtotal

5. **Relaciones:**
   - Debe tener un `proveedor_id` válido
   - Debe tener al menos 1 item

### Ejemplo Coherente:
```
Pedido de compra:
- Proveedor: Distribuidora ABC
- Estado: enviado
- fecha_pedido: 2026-01-25
- fecha_entrega_esperada: 2026-01-30 (5 días)
- Items: 5 items
- Total: $2,500.00
```

---

## 📊 INVENTARIO

### Reglas Principales:
1. **Cantidades:**
   - `cantidad_actual` ≥ 0 (no puede ser negativa)
   - `cantidad_minima` > 0 (amortiguador, nunca 0)
   - Típicamente: `cantidad_minima` = 20-30% de stock normal
   - Si `cantidad_actual` < `cantidad_minima` → alerta de reposición

2. **Unidades:**
   - Debe coincidir con la unidad del item
   - Ejemplos: kg, litros, unidades, qq (quintales)

3. **Costos:**
   - `ultimo_costo_unitario` = último costo registrado del item
   - Se actualiza cuando llega una factura aprobada

4. **Ubicaciones:**
   - Valores típicos: `bodega_principal`, `bodega_secundaria`, `cocina`

### Ejemplo Coherente:
```
Inventario de Pollo:
- cantidad_actual: 150 kg
- cantidad_minima: 50 kg (amortiguador)
- ultimo_costo_unitario: $8.50/kg
- Estado: ✅ Bien (150 > 50)
```

---

## 🍳 RECETAS

### Reglas Principales:
1. **Tipos:**
   - `desayuno`: Platos para desayuno
   - `almuerzo`: Platos para almuerzo
   - `cena`: Platos para cena

2. **Porciones:**
   - `porciones` ≥ 1 (número de porciones que rinde la receta)
   - `porcion_gramos` = peso total de la receta en gramos
   - `calorias_por_porcion` = calorias_totales / porciones
   - `costo_por_porcion` = costo_total / porciones

3. **Ingredientes:**
   - Cada receta debe tener al menos 1 ingrediente
   - `cantidad` debe ser realista según el tipo de ingrediente
   - `unidad` debe coincidir con la unidad del item

4. **Cálculos:**
   - `calorias_totales` = suma de calorías de todos los ingredientes
   - `costo_total` = suma de costos de todos los ingredientes
   - `porcion_gramos` = suma de pesos de todos los ingredientes

### Ejemplo Coherente:
```
Receta: Arroz con Pollo
- Tipo: almuerzo
- Porciones: 10
- Ingredientes: arroz (2 kg), pollo (1.5 kg), verduras (500 g)
- Costo total: $25.00
- Costo por porción: $2.50
- Calorías totales: 3,500
- Calorías por porción: 350
```

---

## 🏢 PROVEEDORES

### Reglas Principales:
1. **Datos Básicos:**
   - `nombre`: Nombre del proveedor
   - `ruc`: RUC único (formato: 1234567890001)
   - `telefono`: Formato típico: +593 99 999 9999
   - `email`: Formato válido de email

2. **Estados:**
   - `activo`: true = proveedor activo, false = inactivo
   - Solo proveedores activos pueden tener pedidos/facturas nuevos

3. **Relaciones:**
   - Un proveedor puede tener múltiples facturas
   - Un proveedor puede tener múltiples pedidos
   - Un proveedor puede proveer múltiples items

---

## 🔗 RELACIONES ENTRE ENTIDADES

### 1. Charolas ↔ Recetas/Items
- Una charola puede tener múltiples items (recetas o items directos)
- Cada item en charola tiene: cantidad, precio_unitario, costo_unitario
- `total_ventas` = suma de (cantidad × precio_unitario)
- `costo_total` = suma de (cantidad × costo_unitario)

### 2. Facturas ↔ Items
- Una factura tiene múltiples items
- Cada item tiene: cantidad_facturada, cantidad_aprobada, precio_unitario
- `subtotal` = suma de (cantidad × precio_unitario)

### 3. Pedidos ↔ Items
- Un pedido tiene múltiples items
- Cada item tiene: cantidad, precio_unitario, subtotal
- `total` = suma de subtotales

### 4. Recetas ↔ Items (Ingredientes)
- Una receta tiene múltiples ingredientes (items)
- Cada ingrediente tiene: cantidad, unidad
- Los cálculos de costo y calorías se hacen sumando ingredientes

### 5. Inventario ↔ Items
- Cada item tiene un registro de inventario (1:1)
- `cantidad_actual` se actualiza con facturas aprobadas y charolas servidas

---

## ✅ VALIDACIONES CRÍTICAS

### Al Generar Datos Mock:

1. **Charolas:**
   - ✅ personas_servidas = número de charolas
   - ✅ total_ventas = suma de items
   - ✅ ganancia = total_ventas - costo_total
   - ✅ tiempo_comida válido (desayuno/almuerzo/cena)

2. **Facturas:**
   - ✅ total = subtotal + iva
   - ✅ iva = subtotal × 0.16 (o el porcentaje correcto)
   - ✅ fecha_emision ≤ fecha_recepcion
   - ✅ cantidad_aprobada ≤ cantidad_facturada

3. **Pedidos:**
   - ✅ total = suma de subtotales
   - ✅ fecha_pedido ≤ fecha_entrega_esperada
   - ✅ estado válido según flujo

4. **Inventario:**
   - ✅ cantidad_minima > 0
   - ✅ cantidad_actual ≥ 0
   - ✅ unidad coincide con item

5. **Recetas:**
   - ✅ costo_por_porcion = costo_total / porciones
   - ✅ calorias_por_porcion = calorias_totales / porciones
   - ✅ tipo válido (desayuno/almuerzo/cena)

---

## 📝 EJEMPLOS DE DATOS COHERENTES

### Ejemplo 1: Charola Completa
```json
{
  "numero_charola": "CHR-20260130-001",
  "fecha_servicio": "2026-01-30T12:00:00",
  "ubicacion": "Restaurante_A",
  "tiempo_comida": "almuerzo",
  "personas_servidas": 1,
  "items": [
    {
      "nombre_item": "Arroz con Pollo",
      "cantidad": 1,
      "precio_unitario": 5.50,
      "costo_unitario": 2.50,
      "subtotal": 5.50,
      "costo_subtotal": 2.50
    }
  ],
  "total_ventas": 5.50,
  "costo_total": 2.50,
  "ganancia": 3.00
}
```

### Ejemplo 2: Factura Coherente
```json
{
  "numero_factura": "FAC-2026-001",
  "tipo": "proveedor",
  "proveedor_id": 1,
  "fecha_emision": "2026-01-25",
  "fecha_recepcion": "2026-01-27",
  "items": [
    {
      "cantidad_facturada": 100,
      "cantidad_aprobada": 100,
      "precio_unitario": 8.50,
      "subtotal": 850.00
    },
    {
      "cantidad_facturada": 50,
      "cantidad_aprobada": 50,
      "precio_unitario": 2.00,
      "subtotal": 100.00
    }
  ],
  "subtotal": 950.00,
  "iva": 152.00,
  "total": 1102.00,
  "estado": "aprobada"
}
```

---

**Última actualización:** 30 de Enero, 2026
