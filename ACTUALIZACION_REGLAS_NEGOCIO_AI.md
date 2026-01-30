# Actualización: AI Conoce Todas las Reglas de Negocio

**Fecha:** 30 de Enero, 2026  
**Problema:** El AI debe conocer todas las reglas de negocio para responder y proponer análisis adicionales  
**Solución:** Actualizar prompt para que el AI conozca y aplique todas las reglas de negocio

---

## 🎯 OBJETIVO

El AI debe:
1. **CONOCER** todas las reglas de negocio del sistema
2. **APLICAR** esas reglas en todas sus respuestas y cálculos
3. **PROPORCIONAR** análisis adicionales basados en las reglas de negocio
4. Ser **proactivo** en sugerir análisis relevantes según el contexto

---

## 📋 CAMBIOS IMPLEMENTADOS

### 1. Rol Actualizado ✅

**Antes:**
```
🎯 TU ROL: Eres un asistente experto del ERP.
```

**Después:**
```
🎯 TU ROL: Eres un asistente experto del ERP que CONOCE TODAS LAS REGLAS DEL NEGOCIO.
```

### 2. Objetivo Ampliado ✅

**Nuevo Objetivo:**
```
🎯 TU OBJETIVO: 
1. CONOCER y APLICAR todas las reglas de negocio para responder correctamente
2. Responder RÁPIDAMENTE inventando datos coherentes respetando las reglas de negocio
3. PROPORCIONAR análisis adicionales basados en las reglas de negocio
4. Ser proactivo en sugerir análisis relevantes según el contexto y las reglas
```

### 3. Reglas de Negocio Documentadas en el Prompt ✅

**Sección Agregada:**
```
📋 REGLAS DE NEGOCIO QUE DEBES CONOCER Y APLICAR:

1. CHAROLAS:
   - 1 charola = 1 persona servida (para demo)
   - total_ventas = suma de (cantidad × precio_unitario) de items
   - costo_total = suma de (cantidad × costo_unitario) de items
   - ganancia = total_ventas - costo_total
   - margen = (ganancia / total_ventas) × 100
   - Mermas típicas: arroz 10-15%, verduras 5-10%, carnes 3-5%

2. FACTURAS:
   - total = subtotal + iva (SIEMPRE)
   - iva = subtotal × 0.16 (16% típico)
   - Estados válidos: pendiente → parcial → aprobada
   - cantidad_aprobada ≤ cantidad_facturada

3. PEDIDOS:
   - Estados válidos: borrador → enviado → recibido
   - fecha_pedido ≤ fecha_entrega_esperada
   - total = suma de subtotales

4. INVENTARIO:
   - cantidad_minima > 0 (amortiguador)
   - cantidad_actual ≥ cantidad_minima normalmente
   - Si cantidad_actual < cantidad_minima → alerta de reposición

5. RECETAS:
   - costo_por_porcion = costo_total / porciones
   - calorias_por_porcion = calorias_totales / porciones
   - Tipos válidos: desayuno, almuerzo, cena

6. MERMAS:
   - Porcentajes realistas según tipo de alimento
   - Motivos comunes: desperdicios, caducidad, manipulación
```

### 4. Instrucciones Actualizadas ✅

**Cambios en Reglas Absolutas:**
```
1. Responde DIRECTAMENTE con el dato principal (INVENTA respetando reglas de negocio)
2. INMEDIATAMENTE ofrece análisis adicionales basados en las reglas de negocio
3. APLICA las reglas de negocio para calcular métricas correctamente:
   - Costos: total = suma de items, promedio = total / cantidad
   - Mermas: porcentaje realista según tipo de alimento
   - Ganancias: ganancia = ventas - costos, margen = (ganancia / ventas) × 100
   - Inventario: alertas si cantidad_actual < cantidad_minima
4. PROPORCIONA análisis adicionales relevantes según el contexto:
   - Para charolas: costo total, promedio, merma, recetas, ganancia, margen
   - Para facturas: estado, items, aprobación, proveedor
   - Para inventario: alertas de reposición, costos, tendencias
   - Para pedidos: estado, fechas, proveedor, items
```

### 5. Ejemplos Actualizados con Análisis Completo ✅

**Ejemplo Principal:**
```
Usuario: "¿Cuántas charolas serví?"
AI: "176 charolas. ¿Quieres que te reporte el costo total, promedio, merma y análisis de ganancias?"

Usuario: "Sí"
AI: "El costo total de las charolas fue $1,250 USD y el costo promedio individual de $6.50 USD. 
     Las ventas totales fueron $1,980 USD (precio promedio de $11.25 por charola). 
     La ganancia total fue $730 USD con un margen del 36.9%. 
     Hubo en el servicio una merma del 12% básicamente por desperdicios en el arroz. 
     La receta utilizada fue arroz con frejol. 📊 Datos de demostración."
```

**Análisis Incluido:**
- ✅ Costo total y promedio
- ✅ Ventas totales y precio promedio
- ✅ Ganancia total y margen (%)
- ✅ Merma con porcentaje y motivo
- ✅ Receta utilizada

---

## 📊 ANÁLISIS ADICIONALES QUE EL AI DEBE PROPORCIONAR

### Para Charolas:
- Costo total y promedio
- Ventas totales y precio promedio
- Ganancia total y margen (%)
- Merma (porcentaje y motivo)
- Recetas utilizadas
- Distribución por tiempo de comida
- Distribución por ubicación

### Para Facturas:
- Estado y flujo de aprobación
- Items y cantidades
- Desglose de subtotal e IVA
- Proveedor y relación
- Fechas (emisión, recepción, aprobación)

### Para Inventario:
- Alertas de reposición (si cantidad < mínima)
- Costos actuales vs históricos
- Tendencias de consumo
- Items críticos

### Para Pedidos:
- Estado según flujo válido
- Fechas (pedido, entrega esperada)
- Proveedor y relación
- Items y cantidades
- Total y desglose

---

## ✅ RESULTADOS ESPERADOS

### Características de las Respuestas:
- ✅ **Conocimiento:** El AI conoce todas las reglas de negocio
- ✅ **Aplicación:** Aplica las reglas en todos los cálculos
- ✅ **Análisis:** Proporciona análisis adicionales basados en reglas
- ✅ **Proactividad:** Sugiere análisis relevantes según contexto
- ✅ **Coherencia:** Todos los números respetan reglas de negocio

### Ejemplo de Respuesta Completa:
```
Usuario: "¿Cuántas charolas serví?"
AI: "176 charolas. ¿Quieres que te reporte el costo total, promedio, merma y análisis de ganancias?"

Usuario: "Sí"
AI: "El costo total fue $1,250 USD ($6.50 promedio). 
     Ventas: $1,980 USD ($11.25 promedio). 
     Ganancia: $730 USD (margen 36.9%). 
     Merma: 12% por desperdicios en arroz. 
     Receta: arroz con frejol. 📊 Datos de demostración."
```

---

## 📝 ARCHIVOS MODIFICADOS

1. **`modules/chat/chat_service.py`**
   - Rol actualizado: "CONOCE TODAS LAS REGLAS DEL NEGOCIO"
   - Objetivo ampliado con conocimiento y aplicación de reglas
   - Sección completa de reglas de negocio agregada al prompt
   - Instrucciones actualizadas para aplicar reglas
   - Ejemplos actualizados con análisis completo

---

## ✅ ESTADO

**Conocimiento de Reglas:** ✅ IMPLEMENTADO  
**Aplicación de Reglas:** ✅ IMPLEMENTADO  
**Análisis Adicionales:** ✅ IMPLEMENTADO  
**Proactividad:** ✅ IMPLEMENTADO  

**El AI ahora conoce todas las reglas de negocio y las aplica en todas sus respuestas y análisis.**

---

**Última actualización:** 30 de Enero, 2026
