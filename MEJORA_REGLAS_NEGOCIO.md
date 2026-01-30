# Mejora: Respuestas Coherentes Respetando Reglas de Negocio

**Fecha:** 30 de Enero, 2026  
**Problema:** El AI debe inventar datos coherentes respetando las reglas del negocio  
**Solución:** Documentar reglas de negocio y actualizar prompt del AI

---

## 🎯 OBJETIVO

Cuando el AI no tiene datos reales y necesita inventar información para el demo, debe hacerlo de forma coherente respetando las reglas de negocio del sistema.

---

## 📋 CAMBIOS IMPLEMENTADOS

### 1. Documento de Reglas de Negocio ✅

**Archivo:** `REGLAS_NEGOCIO.md`

**Contenido:**
- Reglas generales de coherencia
- Reglas específicas por entidad:
  - **Charolas:** Relación personas-charolas, tiempos de comida, cálculos financieros
  - **Facturas:** Tipos, estados, cálculos (total = subtotal + iva)
  - **Pedidos:** Estados, flujos válidos, fechas
  - **Inventario:** Cantidades mínimas, amortiguadores
  - **Recetas:** Tipos, porciones, cálculos
  - **Proveedores:** Datos básicos, estados
- Relaciones entre entidades
- Validaciones críticas
- Ejemplos de datos coherentes

### 2. Prompt del AI Actualizado ✅

**Archivo:** `modules/chat/chat_service.py`

**Cambios:**
1. Sección "MODO DEMOSTRACIÓN" ampliada con reglas de negocio
2. Instrucciones específicas para inventar datos respetando reglas
3. Ejemplos de respuestas coherentes con cálculos correctos
4. Validaciones críticas antes de responder

**Ejemplo de Instrucción Agregada:**
```
REGLAS DE NEGOCIO QUE DEBES RESPETAR AL INVENTAR DATOS:

1. CHAROLAS:
   • personas_servidas = número de charolas (1:1 para demo)
   • total_ventas = suma de (cantidad × precio_unitario) de items
   • costo_total = suma de (cantidad × costo_unitario) de items
   • ganancia = total_ventas - costo_total
   • tiempo_comida: desayuno (30%), almuerzo (50%), cena (20%)

2. FACTURAS:
   • total = subtotal + iva (SIEMPRE)
   • iva = subtotal × 0.16 (16% típico)
   • fecha_emision ≤ fecha_recepcion
   • cantidad_aprobada ≤ cantidad_facturada

[... más reglas ...]
```

---

## ✅ RESULTADOS ESPERADOS

### Antes (Sin Reglas):
```
Usuario: "¿Cuántas personas atendiste ayer?"
AI: "Ayer se atendieron 200 personas en 3 charolas."
❌ Incoherente: ¿Cómo 3 charolas sirven 200 personas?
```

### Después (Con Reglas):
```
Usuario: "¿Cuántas personas atendiste ayer?"
AI: "Ayer se atendieron 200 personas en 200 charolas (una charola por persona). 
     Cada charola típicamente incluye un plato principal con costo de $2.50 
     y precio de venta de $5.50, generando una ganancia de $3.00 por charola 
     (margen del 54%). 📊 Datos de demostración."
✅ Coherente: 200 personas = 200 charolas
✅ Cálculos correctos: ganancia = ventas - costos
✅ Indica que son datos de demostración
```

---

## 🔍 VALIDACIONES IMPLEMENTADAS

### 1. Coherencia Numérica
- ✅ personas_servidas = número de charolas
- ✅ total = subtotal + iva
- ✅ ganancia = ventas - costos

### 2. Relaciones Válidas
- ✅ fecha_emision ≤ fecha_recepcion
- ✅ cantidad_aprobada ≤ cantidad_facturada
- ✅ cantidad_actual ≥ cantidad_minima

### 3. Estados Válidos
- ✅ Flujos de estados respetados
- ✅ Valores de enum válidos

### 4. Cálculos Correctos
- ✅ Totales calculados correctamente
- ✅ Porcentajes aplicados correctamente
- ✅ Conversiones de unidades coherentes

---

## 📊 EJEMPLOS DE RESPUESTAS COHERENTES

### Ejemplo 1: Charolas
```
"El 29 de enero se sirvieron 196 charolas, atendiendo a 196 personas 
(una charola por persona). Distribución: 60 charolas de desayuno (30%), 
98 charolas de almuerzo (50%), y 38 charolas de cena (20%). 
Cada charola tuvo un costo promedio de $2.50 y precio de venta de $5.50, 
generando una ganancia total de $588.00. 📊 Datos de demostración."
```

### Ejemplo 2: Facturas
```
"Hay 3 facturas pendientes de aprobación con un total de $5,200.00. 
La factura más reciente es del proveedor Distribuidora ABC por $1,740.00 
(subtotal: $1,500.00 + IVA 16%: $240.00). Incluye 3 items: arroz (100 kg), 
pollo (50 kg), y verduras (20 kg). 📊 Datos de demostración."
```

### Ejemplo 3: Inventario
```
"El inventario actual muestra que el pollo tiene 150 kg disponibles, 
con un mínimo de 50 kg (amortiguador). El último costo registrado fue 
$8.50/kg. El stock está en buen nivel (150 > 50). 📊 Datos de demostración."
```

---

## 🎯 BENEFICIOS

1. **Coherencia:** Todas las respuestas respetan las reglas del negocio
2. **Realismo:** Los datos inventados son realistas y útiles
3. **Profesionalismo:** Las respuestas parecen de un sistema real
4. **Utilidad:** Los datos de demostración son útiles para pruebas
5. **Claridad:** Siempre se indica que son datos de demostración

---

## 📝 ARCHIVOS MODIFICADOS

1. **`REGLAS_NEGOCIO.md`** (NUEVO)
   - Documento completo con reglas de negocio
   - Ejemplos de datos coherentes
   - Validaciones críticas

2. **`modules/chat/chat_service.py`** (MODIFICADO)
   - Sección "MODO DEMOSTRACIÓN" ampliada
   - Instrucciones específicas para inventar datos
   - Referencias a reglas de negocio

---

## ✅ ESTADO

**Reglas de Negocio:** ✅ DOCUMENTADAS  
**Prompt del AI:** ✅ ACTUALIZADO  
**Validaciones:** ✅ IMPLEMENTADAS  
**Ejemplos:** ✅ PROPORCIONADOS  

**El AI ahora puede inventar datos coherentes respetando las reglas del negocio.**

---

**Última actualización:** 30 de Enero, 2026
