# Verificación de Consistencia de Enums entre Código y Base de Datos

## Resumen Ejecutivo

Este documento verifica la consistencia entre los enums definidos en el código Python y los enums en PostgreSQL.

## 1. Enum `tiporeceta`

### Base de Datos (PostgreSQL)
- **Tipo**: `tiporeceta`
- **Valores esperados**: `'desayuno'`, `'almuerzo'`, `'cena'` (MINÚSCULAS)
- **Tabla**: `recetas`
- **Columna**: `tipo`

### Código Python
- **Clase Enum**: `TipoReceta` en `models/receta.py`
- **Valores**:
  - `DESAYUNO = 'desayuno'`
  - `ALMUERZO = 'almuerzo'`
  - `CENA = 'cena'`
- **Modelo**: Usa `PG_ENUM` directamente con `values_callable=lambda x: [e.value for e in TipoReceta]`
- **Servicio**: `modules/planificacion/recetas.py` convierte a `.value` (minúsculas) antes de insertar
- **to_dict()**: Retorna `.value` (string en minúsculas)

### ✅ Estado: CONSISTENTE
- Código usa valores en minúsculas
- PostgreSQL espera valores en minúsculas
- Servicio convierte correctamente

---

## 2. Enum `tiempocomida`

### Base de Datos (PostgreSQL)
- **Tipo**: `tiempocomida`
- **Valores esperados**: `'desayuno'`, `'almuerzo'`, `'cena'` (MINÚSCULAS)
- **Tabla**: `programacion_menu`
- **Columna**: `tiempo_comida`

### Código Python
- **Clase Enum**: `TiempoComida` en `models/programacion.py`
- **Valores**:
  - `DESAYUNO = 'desayuno'`
  - `ALMUERZO = 'almuerzo'`
  - `CENA = 'cena'`
- **Modelo**: Usa `PG_ENUM` directamente con `values_callable=lambda x: [e.value for e in TiempoComida]`
- **Servicio**: `routes/planificacion_routes.py` convierte a `.value` (minúsculas) antes de insertar
- **to_dict()**: Retorna `.value` (string en minúsculas)

### ✅ Estado: CONSISTENTE (CORREGIDO)
- Código ahora usa valores en minúsculas (corregido)
- PostgreSQL espera valores en minúsculas
- Servicio convierte correctamente a `.value`

---

## 3. Enum `categoriaitem` (si existe)

### Base de Datos (PostgreSQL)
- **Tipo**: `categoriaitem` (verificar si existe)
- **Valores esperados**: Verificar en BD
- **Tabla**: `items`
- **Columna**: `categoria`

### Código Python
- **Clase Enum**: `CategoriaItem` en `models/item.py`
- **Valores**:
  - `MATERIA_PRIMA = 'materia_prima'`
  - `INSUMO = 'insumo'`
  - `PRODUCTO_TERMINADO = 'producto_terminado'`
  - `BEBIDA = 'bebida'`
  - `LIMPIEZA = 'limpieza'`
  - `OTROS = 'otros'`
- **Modelo**: Usa `Enum(CategoriaItem)` de SQLAlchemy (NO PG_ENUM)
- **Servicio**: `modules/logistica/items.py` convierte strings a objetos enum
- **to_dict()**: Retorna `.value` (string)

### ⚠️ Estado: VERIFICAR EN BD
- Si existe enum `categoriaitem` en PostgreSQL, debería usar `PG_ENUM`
- Si NO existe, el uso de `Enum()` de SQLAlchemy es correcto

---

## Instrucciones para Verificar

Ejecuta el script SQL `VERIFICAR_ENUMS_BD.sql` para verificar:

1. Los valores reales de los enums en PostgreSQL
2. Los valores actuales en las tablas
3. Si existe el enum `categoriaitem`

### Comandos SQL a ejecutar:

```sql
-- Verificar enum tiporeceta
SELECT t.typname, e.enumlabel, e.enumsortorder
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'tiporeceta'
ORDER BY e.enumsortorder;

-- Verificar enum tiempocomida
SELECT t.typname, e.enumlabel, e.enumsortorder
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'tiempocomida'
ORDER BY e.enumsortorder;

-- Verificar si existe enum categoriaitem
SELECT t.typname, e.enumlabel, e.enumsortorder
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'categoriaitem'
ORDER BY e.enumsortorder;
```

---

## Correcciones Aplicadas

1. ✅ **Programacion.tiempo_comida**: Cambiado de usar nombres (mayúsculas) a valores (minúsculas)
2. ✅ **routes/planificacion_routes.py**: Actualizado para convertir a `.value` en lugar de `.name`
3. ✅ **TiempoComidaEnum TypeDecorator**: Actualizado comentarios y lógica para reflejar valores en minúsculas

---

## Próximos Pasos

1. Ejecutar `VERIFICAR_ENUMS_BD.sql` en la base de datos
2. Comparar resultados con las expectativas del código
3. Si hay discrepancias, aplicar correcciones necesarias
4. Si `categoriaitem` existe como enum en PostgreSQL, actualizar `Item` para usar `PG_ENUM`
