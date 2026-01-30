# Optimizaciones Adicionales de Consultas

**Fecha:** 30 de Enero, 2026  
**Objetivo:** Optimizaciones avanzadas para mejorar el rendimiento de las consultas del AI

---

## 🚀 Optimizaciones Implementadas

### 1. LIMIT Automático Inteligente

**Problema:** El AI a veces genera consultas sin LIMIT, lo que puede traer miles de filas.

**Solución:**
- Detección automática de consultas sin LIMIT
- Agregación automática de `LIMIT 100` para consultas de selección simple
- No se agrega LIMIT si la consulta ya tiene agregaciones (COUNT, SUM, etc.)

**Código:**
```python
# Detectar consultas potencialmente costosas sin LIMIT
if 'SELECT' in query_upper and 'LIMIT' not in query_upper:
    if not any(keyword in query_upper for keyword in ['COUNT(', 'SUM(', 'AVG(', 'MAX(', 'MIN(', 'GROUP BY']):
        query = query.rstrip(';').strip() + ' LIMIT 100'
```

---

### 2. Monitoreo de Rendimiento Mejorado

**Mejoras:**
- Umbral más estricto: consultas lentas ahora se detectan a los 3 segundos (antes 5)
- Información de rendimiento incluida en los resultados
- Indicadores visuales de rendimiento:
  - ⚡ < 100ms: rápida
  - ⏱️ 100-1000ms: normal
  - 🐌 > 1000ms: lenta (sugiere optimizar)

**Código:**
```python
info_optimizacion = {
    'tiempo_ejecucion_ms': round(tiempo_ejecucion * 1000, 2),
    'total_filas': len(resultados),
    'usa_indices': any(campo in query_upper for campo in ['id', 'activo', 'estado', 'fecha_', 'proveedor_id', 'item_id'])
}
```

---

### 3. Sugerencias Automáticas de Optimización

**Características:**
- Detecta cuando una consulta no usa índices conocidos
- Sugiere usar campos indexados en WHERE
- Sugiere usar JOINs con foreign keys indexadas
- Logs informativos para debugging

**Ejemplo:**
```
⚠️ Consulta lenta detectada: 3.5s
💡 Sugerencias de optimización: Considera usar campos indexados en WHERE (id, activo, estado, fecha_*, proveedor_id, item_id)
```

---

### 4. Límites Inteligentes de Visualización

**Optimización:**
- Ajusta el número de filas mostradas según el tipo de consulta:
  - ≤ 20 filas: muestra todas
  - Agregaciones (COUNT, SUM): hasta 30 filas
  - Listas simples: máximo 15 filas

**Código:**
```python
if total <= 20:
    max_filas_mostrar = total
elif any(keyword in consulta_upper for keyword in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']):
    max_filas_mostrar = min(30, total)
else:
    max_filas_mostrar = min(15, total)
```

---

### 5. Guías de Optimización en el Prompt

Se agregaron guías avanzadas de optimización al prompt del sistema:

#### Optimizaciones Avanzadas:
1. **Consultas Agrupadas (GROUP BY):**
   - Usa GROUP BY con campos indexados
   - Evita GROUP BY en campos calculados

2. **Subconsultas VS JOINs:**
   - Prefiere JOINs sobre subconsultas
   - Usa EXISTS() en lugar de IN() para subconsultas grandes

3. **Índices Compuestos:**
   - Usa múltiples campos indexados en WHERE
   - Ejemplo: `WHERE estado = 'pendiente' AND fecha >= '2026-01-01'`

4. **Evitar Operaciones Costosas:**
   - Evita funciones en WHERE cuando sea posible
   - Usa rangos de fechas en lugar de DATE() cuando sea apropiado

5. **Límites Inteligentes:**
   - Listas: LIMIT 20-50
   - Agregaciones: sin LIMIT (ya agrupa)
   - Búsquedas: LIMIT 10-20

---

## 📊 Comparación Antes/Después

### Antes:
- Consultas sin LIMIT podían traer miles de filas
- No había monitoreo de rendimiento visible
- No había sugerencias de optimización
- Límite fijo de 15 filas siempre

### Después:
- LIMIT automático agregado cuando falta
- Monitoreo de rendimiento con indicadores visuales
- Sugerencias automáticas de optimización
- Límites inteligentes según tipo de consulta

---

## 🎯 Beneficios

1. **Rendimiento Mejorado:**
   - Consultas más rápidas con LIMIT automático
   - Menos carga en la base de datos
   - Mejor uso de índices

2. **Mejor Experiencia:**
   - Indicadores visuales de rendimiento
   - Respuestas más rápidas
   - Información más relevante mostrada

3. **Optimización Continua:**
   - Logs de consultas lentas
   - Sugerencias automáticas
   - Guías en el prompt para el AI

---

## 🔄 Próximas Optimizaciones Posibles

### 1. Caché de Consultas Frecuentes
- Cachear consultas comunes como "charolas de hoy"
- TTL corto (5-10 minutos)
- Invalidación automática

### 2. Análisis EXPLAIN Automático
- Ejecutar EXPLAIN ANALYZE para consultas lentas
- Analizar el plan de ejecución
- Sugerir índices faltantes

### 3. Consultas Preparadas
- Pre-compilar consultas comunes
- Reutilizar planes de ejecución
- Reducir overhead de parsing

### 4. Estadísticas de Uso
- Trackear qué consultas son más comunes
- Identificar patrones de uso
- Optimizar índices según uso real

### 5. Validación Previa de Costo
- Estimar costo de consulta antes de ejecutar
- Rechazar consultas muy costosas
- Sugerir alternativas más eficientes

---

## 📝 Notas Técnicas

- **LIMIT automático:** Solo se agrega si no hay agregaciones (COUNT, SUM, etc.)
- **Monitoreo:** Los logs se guardan con nivel WARNING para consultas > 3s
- **Rendimiento:** La información de tiempo se incluye en los resultados para el AI
- **Sugerencias:** Se generan automáticamente basadas en análisis de la consulta

---

**Estado:** ✅ Optimizaciones implementadas y funcionando
