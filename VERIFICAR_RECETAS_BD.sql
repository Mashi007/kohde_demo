-- ============================================================================
-- SCRIPT DE VERIFICACIÓN: Tabla de Recetas y Enum tiporeceta
-- ============================================================================
-- Este script ayuda a verificar la estructura y datos de la tabla de recetas
-- y el enum tiporeceta en PostgreSQL

-- ============================================================================
-- 1. VERIFICAR ESTRUCTURA DEL ENUM tiporeceta
-- ============================================================================

-- Ver los valores del enum tiporeceta
SELECT 
    t.typname AS enum_name,
    e.enumlabel AS enum_value,
    e.enumsortorder AS sort_order
FROM pg_type t 
JOIN pg_enum e ON t.oid = e.enumtypid  
WHERE t.typname = 'tiporeceta'
ORDER BY e.enumsortorder;

-- ============================================================================
-- 2. VERIFICAR ESTRUCTURA DE LA TABLA recetas
-- ============================================================================

-- Ver la estructura de la tabla recetas
SELECT 
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'recetas'
ORDER BY ordinal_position;

-- Ver información detallada de la columna tipo
SELECT 
    c.column_name,
    c.data_type,
    c.udt_name,
    c.character_maximum_length,
    c.is_nullable,
    c.column_default,
    CASE 
        WHEN c.udt_name = 'USER-DEFINED' THEN 
            (SELECT string_agg(e.enumlabel, ', ' ORDER BY e.enumsortorder)
             FROM pg_type t 
             JOIN pg_enum e ON t.oid = e.enumtypid  
             WHERE t.typname = c.udt_name)
        ELSE NULL
    END AS enum_values
FROM information_schema.columns c
WHERE c.table_name = 'recetas' 
  AND c.column_name = 'tipo';

-- ============================================================================
-- 3. VERIFICAR DATOS EN LA TABLA recetas
-- ============================================================================

-- Ver todas las recetas con su tipo
SELECT 
    id,
    nombre,
    tipo,
    porciones,
    activa,
    fecha_creacion
FROM recetas
ORDER BY fecha_creacion DESC
LIMIT 20;

-- Contar recetas por tipo
SELECT 
    tipo,
    COUNT(*) AS cantidad,
    COUNT(*) FILTER (WHERE activa = true) AS activas,
    COUNT(*) FILTER (WHERE activa = false) AS inactivas
FROM recetas
GROUP BY tipo
ORDER BY tipo;

-- Ver recetas con valores problemáticos (si los hay)
SELECT 
    id,
    nombre,
    tipo,
    pg_typeof(tipo) AS tipo_dato,
    CASE 
        WHEN tipo::text NOT IN ('desayuno', 'almuerzo', 'cena') 
        THEN 'VALOR INVÁLIDO' 
        ELSE 'OK' 
    END AS estado_validacion
FROM recetas
WHERE tipo::text NOT IN ('desayuno', 'almuerzo', 'cena')
   OR tipo IS NULL;

-- ============================================================================
-- 4. VERIFICAR CONSTRAINTS Y RESTRICCIONES
-- ============================================================================

-- Ver constraints de la tabla recetas
SELECT
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    tc.table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.table_name = 'recetas'
ORDER BY tc.constraint_type, kcu.column_name;

-- Ver el check constraint del enum (si existe)
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'recetas'::regclass
  AND contype = 'c';

-- ============================================================================
-- 5. PRUEBAS DE INSERCIÓN (SOLO PARA DEBUG - NO EJECUTAR EN PRODUCCIÓN)
-- ============================================================================

-- NOTA: Estas consultas son solo para verificar que el enum funciona correctamente
-- NO las ejecutes en producción sin hacer backup primero

-- Probar insertar con diferentes formatos (comentado por seguridad)
/*
-- Probar con valor en minúsculas (debería funcionar)
INSERT INTO recetas (nombre, tipo, porciones, activa)
VALUES ('Test Minúsculas', 'almuerzo', 1, true);

-- Probar con valor en mayúsculas (debería fallar si el enum no lo acepta)
INSERT INTO recetas (nombre, tipo, porciones, activa)
VALUES ('Test Mayúsculas', 'ALMUERZO', 1, true);

-- Verificar los inserts
SELECT id, nombre, tipo FROM recetas WHERE nombre LIKE 'Test%';

-- Limpiar pruebas (descomentar solo después de verificar)
-- DELETE FROM recetas WHERE nombre LIKE 'Test%';
*/

-- ============================================================================
-- 6. VERIFICAR ÍNDICES
-- ============================================================================

-- Ver índices de la tabla recetas
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'recetas';

-- ============================================================================
-- 7. RESUMEN DE VERIFICACIÓN
-- ============================================================================

-- Resumen completo
SELECT 
    'Total de recetas' AS metrica,
    COUNT(*)::text AS valor
FROM recetas
UNION ALL
SELECT 
    'Recetas activas',
    COUNT(*)::text
FROM recetas
WHERE activa = true
UNION ALL
SELECT 
    'Tipos únicos',
    COUNT(DISTINCT tipo)::text
FROM recetas
UNION ALL
SELECT 
    'Valores del enum',
    string_agg(DISTINCT tipo::text, ', ' ORDER BY tipo::text)
FROM recetas;
