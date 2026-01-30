# 🔍 Instrucciones para Verificar Recetas en la Base de Datos

## 📋 Opciones de Verificación

Tienes dos formas de verificar el estado de la tabla `recetas` y el enum `tiporeceta`:

---

## 🔧 Opción 1: Script SQL (Recomendado para análisis detallado)

### Pasos:

1. **Conectarte a la base de datos PostgreSQL en Render:**
   - Ve al dashboard de Render
   - Selecciona tu base de datos PostgreSQL
   - Ve a la pestaña **"Connect"** o **"Info"**
   - Copia la **Connection String** o usa las credenciales

2. **Ejecutar el script SQL:**
   - Abre `VERIFICAR_RECETAS_BD.sql`
   - Copia y pega las consultas en tu cliente SQL (pgAdmin, DBeaver, psql, etc.)
   - O ejecuta sección por sección según lo que necesites verificar

### Qué verifica el script SQL:

- ✅ Valores del enum `tiporeceta`
- ✅ Estructura de la tabla `recetas`
- ✅ Datos actuales en la tabla
- ✅ Conteo de recetas por tipo
- ✅ Valores problemáticos o inválidos
- ✅ Constraints y restricciones
- ✅ Índices de la tabla

---

## 🐍 Opción 2: Script Python (Más fácil y rápido)

### Pasos:

1. **Ejecutar el script desde la terminal:**
```bash
# Desde la raíz del proyecto
python scripts/verificar_recetas_bd.py
```

2. **O desde Render (si tienes acceso SSH):**
```bash
# Conectarte al servicio del backend
# Luego ejecutar:
cd /opt/render/project/src
python scripts/verificar_recetas_bd.py
```

### Qué muestra el script Python:

- ✅ Valores del enum `tiporeceta`
- ✅ Estructura de la tabla `recetas`
- ✅ Últimas 10 recetas creadas
- ✅ Conteo por tipo de receta
- ✅ Valores problemáticos o inválidos
- ✅ Resumen general

---

## 📊 Qué Buscar en los Resultados

### ✅ Valores Correctos del Enum:

El enum `tiporeceta` debe tener estos valores (en minúsculas):
- `desayuno`
- `almuerzo`
- `cena`

### ⚠️ Problemas Comunes:

1. **Enum con valores en mayúsculas:**
   - Si ves `DESAYUNO`, `ALMUERZO`, `CENA` en lugar de minúsculas
   - **Solución**: El código ya maneja esto, pero puede requerir migración

2. **Valores NULL en la columna tipo:**
   - Si hay recetas con `tipo = NULL`
   - **Solución**: Actualizar esas recetas con un valor válido

3. **Valores inválidos:**
   - Si hay valores que no son `desayuno`, `almuerzo` o `cena`
   - **Solución**: Corregir esos valores manualmente

---

## 🔧 Consultas SQL Rápidas (Copiar y Pegar)

### Ver todas las recetas:
```sql
SELECT id, nombre, tipo, porciones, activa 
FROM recetas 
ORDER BY fecha_creacion DESC;
```

### Ver valores del enum:
```sql
SELECT e.enumlabel AS valor
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'tiporeceta'
ORDER BY e.enumsortorder;
```

### Contar por tipo:
```sql
SELECT tipo, COUNT(*) AS cantidad
FROM recetas
GROUP BY tipo;
```

### Buscar valores problemáticos:
```sql
SELECT id, nombre, tipo
FROM recetas
WHERE tipo::text NOT IN ('desayuno', 'almuerzo', 'cena')
   OR tipo IS NULL;
```

---

## 🛠️ Solución de Problemas

### Si el enum tiene valores incorrectos:

1. **Verificar el enum actual:**
```sql
SELECT e.enumlabel 
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'tiporeceta';
```

2. **Si necesitas recrear el enum (CUIDADO - Solo si es necesario):**
```sql
-- ⚠️ ADVERTENCIA: Esto requiere eliminar y recrear el enum
-- Solo hazlo si realmente es necesario y después de hacer backup

-- 1. Cambiar la columna a texto temporalmente
ALTER TABLE recetas ALTER COLUMN tipo TYPE text;

-- 2. Eliminar el enum antiguo
DROP TYPE IF EXISTS tiporeceta;

-- 3. Crear el enum con los valores correctos
CREATE TYPE tiporeceta AS ENUM ('desayuno', 'almuerzo', 'cena');

-- 4. Cambiar la columna de vuelta al enum
ALTER TABLE recetas ALTER COLUMN tipo TYPE tiporeceta USING tipo::tiporeceta;
```

### Si hay valores NULL:

```sql
-- Actualizar recetas con tipo NULL a 'almuerzo' (valor por defecto)
UPDATE recetas 
SET tipo = 'almuerzo'::tiporeceta 
WHERE tipo IS NULL;
```

### Si hay valores inválidos:

```sql
-- Ver qué valores inválidos hay
SELECT DISTINCT tipo::text 
FROM recetas 
WHERE tipo::text NOT IN ('desayuno', 'almuerzo', 'cena');

-- Corregir valores específicos (ejemplo: si hay 'ALMUERZO' en mayúsculas)
UPDATE recetas 
SET tipo = 'almuerzo'::tiporeceta 
WHERE tipo::text = 'ALMUERZO';
```

---

## 📝 Notas Importantes

1. **Backup antes de cambios:** Siempre haz backup de la base de datos antes de hacer cambios manuales
2. **Valores en minúsculas:** El enum debe usar valores en minúsculas (`desayuno`, `almuerzo`, `cena`)
3. **El código maneja ambos:** El código del backend ahora acepta tanto minúsculas como mayúsculas y los convierte correctamente
4. **Frontend envía mayúsculas:** El frontend ahora envía `ALMUERZO`, `DESAYUNO`, `CENA` pero el backend los convierte a minúsculas

---

## ✅ Verificación Exitosa

Si todo está correcto, deberías ver:
- ✅ Enum con valores: `desayuno`, `almuerzo`, `cena`
- ✅ Todas las recetas tienen valores válidos
- ✅ No hay valores NULL
- ✅ No hay valores inválidos

Si encuentras algún problema, usa las consultas de solución de problemas arriba.
