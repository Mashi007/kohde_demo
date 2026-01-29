-- ============================================================================
-- SCRIPT CONSOLIDADO: EJECUTAR TODO EN ORDEN
-- Para ejecutar en DBeaver - PostgreSQL
-- ============================================================================
-- Este script ejecuta todos los pasos necesarios en el orden correcto
-- ⚠️ IMPORTANTE: Ejecutar completo de una vez
-- ============================================================================

-- ============================================================================
-- PASO 1: CREAR TABLAS BASE DE RECETAS Y PROGRAMACIÓN
-- ============================================================================
-- Creando tablas base...

-- Crear ENUMs
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tiporeceta') THEN
        CREATE TYPE tiporeceta AS ENUM ('desayuno', 'almuerzo', 'merienda');
        RAISE NOTICE 'ENUM tiporeceta creado';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tiempocomida') THEN
        CREATE TYPE tiempocomida AS ENUM ('desayuno', 'almuerzo', 'cena');
        RAISE NOTICE 'ENUM tiempocomida creado';
    END IF;
END $$;

-- Crear tabla recetas
CREATE TABLE IF NOT EXISTS recetas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo tiporeceta NOT NULL DEFAULT 'almuerzo',
    porciones INTEGER NOT NULL DEFAULT 1,
    porcion_gramos NUMERIC(10, 2),
    calorias_totales NUMERIC(10, 2),
    costo_total NUMERIC(10, 2),
    calorias_por_porcion NUMERIC(10, 2),
    costo_por_porcion NUMERIC(10, 2),
    tiempo_preparacion INTEGER,
    activa BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_recetas_nombre ON recetas(nombre);
CREATE INDEX IF NOT EXISTS idx_recetas_activa ON recetas(activa);
CREATE INDEX IF NOT EXISTS idx_recetas_tipo ON recetas(tipo);

-- Crear tabla receta_ingredientes
CREATE TABLE IF NOT EXISTS receta_ingredientes (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    cantidad NUMERIC(10, 2) NOT NULL,
    unidad VARCHAR(20) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_receta_ingredientes_receta ON receta_ingredientes(receta_id);
CREATE INDEX IF NOT EXISTS idx_receta_ingredientes_item ON receta_ingredientes(item_id);

-- Crear tabla programacion_menu
CREATE TABLE IF NOT EXISTS programacion_menu (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tiempo_comida tiempocomida NOT NULL DEFAULT 'almuerzo',
    ubicacion VARCHAR(100) NOT NULL,
    personas_estimadas INTEGER NOT NULL DEFAULT 0,
    charolas_planificadas INTEGER NOT NULL DEFAULT 0,
    charolas_producidas INTEGER NOT NULL DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_programacion_fecha ON programacion_menu(fecha);
CREATE INDEX IF NOT EXISTS idx_programacion_ubicacion ON programacion_menu(ubicacion);
CREATE INDEX IF NOT EXISTS idx_programacion_tiempo_comida ON programacion_menu(tiempo_comida);

-- Crear tabla programacion_menu_items
CREATE TABLE IF NOT EXISTS programacion_menu_items (
    id SERIAL PRIMARY KEY,
    programacion_id INTEGER NOT NULL REFERENCES programacion_menu(id) ON DELETE CASCADE,
    receta_id INTEGER NOT NULL REFERENCES recetas(id),
    cantidad_porciones INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_programacion_items_programacion ON programacion_menu_items(programacion_id);
CREATE INDEX IF NOT EXISTS idx_programacion_items_receta ON programacion_menu_items(receta_id);

-- ✓ Paso 1 completado

-- ============================================================================
-- PASO 2: ACTUALIZAR CHAROLAS Y MERMAS CON RELACIONES
-- ============================================================================
-- Actualizando charolas y mermas...

-- Agregar charolas_producidas a programacion_menu (si no existe)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'programacion_menu' AND column_name = 'charolas_producidas'
    ) THEN
        ALTER TABLE programacion_menu ADD COLUMN charolas_producidas INTEGER NOT NULL DEFAULT 0;
    END IF;
END $$;

-- Agregar programacion_id a charolas
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'charolas' AND column_name = 'programacion_id'
    ) THEN
        ALTER TABLE charolas ADD COLUMN programacion_id INTEGER REFERENCES programacion_menu(id);
        CREATE INDEX IF NOT EXISTS idx_charolas_programacion ON charolas(programacion_id);
    END IF;
END $$;

-- Crear tabla mermas_receta_programacion
CREATE TABLE IF NOT EXISTS mermas_receta_programacion (
    id SERIAL PRIMARY KEY,
    programacion_id INTEGER NOT NULL REFERENCES programacion_menu(id) ON DELETE CASCADE,
    receta_id INTEGER NOT NULL REFERENCES recetas(id),
    cantidad NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unidad VARCHAR(20) NOT NULL DEFAULT 'g',
    costo_unitario NUMERIC(10, 2) NOT NULL DEFAULT 0,
    costo_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    motivo TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    registrado_por INTEGER,
    UNIQUE(programacion_id, receta_id)
);

CREATE INDEX IF NOT EXISTS idx_mermas_receta_prog_programacion ON mermas_receta_programacion(programacion_id);
CREATE INDEX IF NOT EXISTS idx_mermas_receta_prog_receta ON mermas_receta_programacion(receta_id);
CREATE INDEX IF NOT EXISTS idx_mermas_receta_prog_fecha ON mermas_receta_programacion(fecha_registro);

-- Agregar campos opcionales a mermas (compatibilidad)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mermas' AND column_name = 'programacion_id'
    ) THEN
        ALTER TABLE mermas ADD COLUMN programacion_id INTEGER REFERENCES programacion_menu(id);
        CREATE INDEX IF NOT EXISTS idx_mermas_programacion ON mermas(programacion_id);
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'mermas' AND column_name = 'receta_id'
    ) THEN
        ALTER TABLE mermas ADD COLUMN receta_id INTEGER REFERENCES recetas(id);
        CREATE INDEX IF NOT EXISTS idx_mermas_receta ON mermas(receta_id);
    END IF;
END $$;

-- ✓ Paso 2 completado

-- ============================================================================
-- PASO 3: CREAR VISTAS PARA MÉTRICAS
-- ============================================================================
-- Creando vistas de métricas...

-- Vista 1: Métricas de charolas por programación
CREATE OR REPLACE VIEW vista_metricas_charolas AS
SELECT 
    pm.id AS programacion_id,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    pm.charolas_planificadas,
    pm.charolas_producidas,
    (pm.charolas_producidas - pm.charolas_planificadas) AS diferencia_charolas,
    CASE 
        WHEN pm.charolas_planificadas > 0 THEN 
            ROUND((pm.charolas_producidas::NUMERIC / pm.charolas_planificadas::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_cumplimiento,
    COUNT(DISTINCT c.id) AS total_charolas_registradas,
    COALESCE(SUM(c.personas_servidas), 0) AS total_personas_servidas,
    COALESCE(SUM(c.total_ventas), 0) AS total_ventas,
    COALESCE(SUM(c.costo_total), 0) AS total_costo,
    COALESCE(SUM(c.ganancia), 0) AS total_ganancia,
    CASE 
        WHEN COUNT(DISTINCT c.id) > 0 THEN 
            ROUND(COALESCE(SUM(c.total_ventas), 0) / COUNT(DISTINCT c.id), 2)
        ELSE 0
    END AS promedio_ventas_por_charola,
    CASE 
        WHEN COUNT(DISTINCT c.id) > 0 THEN 
            ROUND(COALESCE(SUM(c.ganancia), 0) / COUNT(DISTINCT c.id), 2)
        ELSE 0
    END AS promedio_ganancia_por_charola
FROM programacion_menu pm
LEFT JOIN charolas c ON c.programacion_id = pm.id
GROUP BY 
    pm.id, 
    pm.fecha, 
    pm.tiempo_comida, 
    pm.ubicacion, 
    pm.charolas_planificadas, 
    pm.charolas_producidas;

-- Vista 2: Resumen de charolas por período
CREATE OR REPLACE VIEW vista_resumen_charolas_periodo AS
SELECT 
    DATE_TRUNC('day', pm.fecha) AS fecha,
    pm.ubicacion,
    pm.tiempo_comida,
    COUNT(DISTINCT pm.id) AS total_programaciones,
    SUM(pm.charolas_planificadas) AS total_charolas_planificadas,
    SUM(pm.charolas_producidas) AS total_charolas_producidas,
    COUNT(DISTINCT c.id) AS total_charolas_registradas,
    SUM(c.personas_servidas) AS total_personas_servidas,
    SUM(c.total_ventas) AS total_ventas,
    SUM(c.costo_total) AS total_costo,
    SUM(c.ganancia) AS total_ganancia,
    CASE 
        WHEN SUM(pm.charolas_planificadas) > 0 THEN 
            ROUND((SUM(pm.charolas_producidas)::NUMERIC / SUM(pm.charolas_planificadas)::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_cumplimiento,
    CASE 
        WHEN COUNT(DISTINCT c.id) > 0 THEN 
            ROUND(SUM(c.total_ventas) / COUNT(DISTINCT c.id), 2)
        ELSE 0
    END AS promedio_ventas_por_charola,
    CASE 
        WHEN COUNT(DISTINCT c.id) > 0 THEN 
            ROUND(SUM(c.ganancia) / COUNT(DISTINCT c.id), 2)
        ELSE 0
    END AS promedio_ganancia_por_charola
FROM programacion_menu pm
LEFT JOIN charolas c ON c.programacion_id = pm.id
GROUP BY 
    DATE_TRUNC('day', pm.fecha),
    pm.ubicacion,
    pm.tiempo_comida;

-- Vista 3: Métricas de mermas por receta
CREATE OR REPLACE VIEW vista_metricas_mermas_receta AS
SELECT 
    mrp.id AS merma_id,
    mrp.programacion_id,
    mrp.receta_id,
    r.nombre AS nombre_receta,
    r.tipo AS tipo_receta,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    mrp.cantidad AS cantidad_merma,
    mrp.unidad,
    mrp.costo_unitario,
    mrp.costo_total AS costo_total_merma,
    mrp.motivo,
    mrp.fecha_registro,
    pmi.cantidad_porciones AS porciones_programadas,
    r.costo_por_porcion,
    r.calorias_por_porcion,
    CASE 
        WHEN pmi.cantidad_porciones > 0 AND r.porcion_gramos > 0 THEN
            ROUND((mrp.cantidad::NUMERIC / (pmi.cantidad_porciones * r.porcion_gramos)::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_merma_sobre_programado
FROM mermas_receta_programacion mrp
INNER JOIN programacion_menu pm ON pm.id = mrp.programacion_id
INNER JOIN recetas r ON r.id = mrp.receta_id
LEFT JOIN programacion_menu_items pmi ON pmi.programacion_id = pm.id AND pmi.receta_id = r.id;

-- Vista 4: Resumen de mermas por programación
CREATE OR REPLACE VIEW vista_resumen_mermas_programacion AS
SELECT 
    pm.id AS programacion_id,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    COUNT(DISTINCT mrp.receta_id) AS total_recetas_con_merma,
    SUM(mrp.cantidad) AS total_cantidad_merma,
    MAX(mrp.unidad) AS unidad_merma,
    SUM(mrp.costo_total) AS total_costo_merma,
    pm.costo_total AS costo_total_programado,
    CASE 
        WHEN pm.costo_total > 0 THEN 
            ROUND((SUM(mrp.costo_total) / pm.costo_total) * 100, 2)
        ELSE 0
    END AS porcentaje_merma_sobre_costo_programado,
    pm.charolas_planificadas,
    pm.charolas_producidas,
    CASE 
        WHEN pm.charolas_planificadas > 0 THEN 
            ROUND((pm.charolas_producidas::NUMERIC / pm.charolas_planificadas::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_cumplimiento_charolas
FROM programacion_menu pm
LEFT JOIN mermas_receta_programacion mrp ON mrp.programacion_id = pm.id
GROUP BY 
    pm.id,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    pm.costo_total,
    pm.charolas_planificadas,
    pm.charolas_producidas;

-- Vista 5: Resumen de mermas por receta (acumulado)
CREATE OR REPLACE VIEW vista_resumen_mermas_por_receta AS
SELECT 
    r.id AS receta_id,
    r.nombre AS nombre_receta,
    r.tipo AS tipo_receta,
    COUNT(DISTINCT mrp.programacion_id) AS total_servicios_con_merma,
    SUM(mrp.cantidad) AS total_cantidad_merma,
    MAX(mrp.unidad) AS unidad_merma,
    SUM(mrp.costo_total) AS total_costo_merma,
    AVG(mrp.cantidad) AS promedio_cantidad_merma,
    AVG(mrp.costo_total) AS promedio_costo_merma,
    MIN(mrp.cantidad) AS minimo_cantidad_merma,
    MAX(mrp.cantidad) AS maximo_cantidad_merma,
    r.costo_por_porcion,
    r.calorias_por_porcion,
    r.porcion_gramos
FROM recetas r
INNER JOIN mermas_receta_programacion mrp ON mrp.receta_id = r.id
GROUP BY 
    r.id,
    r.nombre,
    r.tipo,
    r.costo_por_porcion,
    r.calorias_por_porcion,
    r.porcion_gramos;

-- Vista 6: Comparativa charolas vs mermas
CREATE OR REPLACE VIEW vista_comparativa_charolas_mermas AS
SELECT 
    pm.id AS programacion_id,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    pm.charolas_planificadas,
    pm.charolas_producidas,
    CASE 
        WHEN pm.charolas_planificadas > 0 THEN 
            ROUND((pm.charolas_producidas::NUMERIC / pm.charolas_planificadas::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_cumplimiento_charolas,
    COUNT(DISTINCT c.id) AS charolas_registradas,
    COALESCE(SUM(c.total_ventas), 0) AS total_ventas,
    COALESCE(SUM(c.ganancia), 0) AS total_ganancia,
    COUNT(DISTINCT mrp.receta_id) AS recetas_con_merma,
    COALESCE(SUM(mrp.cantidad), 0) AS total_cantidad_merma,
    COALESCE(SUM(mrp.costo_total), 0) AS total_costo_merma,
    pm.costo_total AS costo_programado,
    CASE 
        WHEN pm.costo_total > 0 THEN 
            ROUND((COALESCE(SUM(mrp.costo_total), 0) / pm.costo_total) * 100, 2)
        ELSE 0
    END AS porcentaje_merma_sobre_costo,
    (COALESCE(SUM(c.ganancia), 0) - COALESCE(SUM(mrp.costo_total), 0)) AS ganancia_neta_ajustada
FROM programacion_menu pm
LEFT JOIN charolas c ON c.programacion_id = pm.id
LEFT JOIN mermas_receta_programacion mrp ON mrp.programacion_id = pm.id
GROUP BY 
    pm.id,
    pm.fecha,
    pm.tiempo_comida,
    pm.ubicacion,
    pm.charolas_planificadas,
    pm.charolas_producidas,
    pm.costo_total;

-- Vista 7: Reporte diario
CREATE OR REPLACE VIEW vista_reporte_diario AS
SELECT 
    DATE_TRUNC('day', pm.fecha) AS fecha,
    pm.ubicacion,
    pm.tiempo_comida,
    COUNT(DISTINCT pm.id) AS servicios_programados,
    SUM(pm.charolas_planificadas) AS charolas_planificadas,
    SUM(pm.charolas_producidas) AS charolas_producidas,
    COUNT(DISTINCT c.id) AS charolas_registradas,
    SUM(c.personas_servidas) AS personas_servidas,
    SUM(c.total_ventas) AS ventas_totales,
    SUM(c.costo_total) AS costo_total_charolas,
    SUM(c.ganancia) AS ganancia_total_charolas,
    COUNT(DISTINCT mrp.receta_id) AS recetas_con_merma,
    SUM(mrp.cantidad) AS cantidad_total_merma,
    SUM(mrp.costo_total) AS costo_total_merma,
    CASE 
        WHEN SUM(pm.charolas_planificadas) > 0 THEN 
            ROUND((SUM(pm.charolas_producidas)::NUMERIC / SUM(pm.charolas_planificadas)::NUMERIC) * 100, 2)
        ELSE 0
    END AS porcentaje_cumplimiento,
    CASE 
        WHEN COUNT(DISTINCT c.id) > 0 THEN 
            ROUND(SUM(c.total_ventas) / COUNT(DISTINCT c.id), 2)
        ELSE 0
    END AS promedio_venta_por_charola,
    CASE 
        WHEN SUM(pm.costo_total) > 0 THEN 
            ROUND((COALESCE(SUM(mrp.costo_total), 0) / SUM(pm.costo_total)) * 100, 2)
        ELSE 0
    END AS porcentaje_merma_sobre_costo
FROM programacion_menu pm
LEFT JOIN charolas c ON c.programacion_id = pm.id
LEFT JOIN mermas_receta_programacion mrp ON mrp.programacion_id = pm.id
GROUP BY 
    DATE_TRUNC('day', pm.fecha),
    pm.ubicacion,
    pm.tiempo_comida;

-- ✓ Paso 3 completado

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================
-- Verificando tablas y vistas creadas...

-- Verificar tablas creadas
SELECT 'Tablas creadas:' as verificacion;
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('recetas', 'receta_ingredientes', 'programacion_menu', 'programacion_menu_items', 'mermas_receta_programacion')
ORDER BY table_name;

-- Verificar vistas creadas
SELECT 'Vistas creadas:' as verificacion;
SELECT viewname FROM pg_views 
WHERE schemaname = 'public' AND viewname LIKE 'vista_%'
ORDER BY viewname;

-- ============================================================================
-- ✅ PROCESO COMPLETADO
-- ============================================================================
-- Puedes ahora usar las vistas para consultar métricas:
--   SELECT * FROM vista_metricas_charolas;
--   SELECT * FROM vista_reporte_diario;
-- ============================================================================
