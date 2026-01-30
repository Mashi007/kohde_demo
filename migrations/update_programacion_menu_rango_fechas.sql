-- ============================================================================
-- MIGRACIÓN: ACTUALIZAR PROGRAMACION_MENU PARA RANGO DE FECHAS
-- ============================================================================
-- Cambia la columna 'fecha' única por 'fecha_desde' y 'fecha_hasta'
-- para permitir programaciones con rangos de fechas
-- ============================================================================

-- 1. Agregar nuevas columnas
ALTER TABLE programacion_menu 
ADD COLUMN IF NOT EXISTS fecha_desde DATE,
ADD COLUMN IF NOT EXISTS fecha_hasta DATE;

-- 2. Migrar datos existentes: usar la fecha actual como fecha_desde y fecha_hasta
UPDATE programacion_menu 
SET fecha_desde = fecha,
    fecha_hasta = fecha
WHERE fecha_desde IS NULL OR fecha_hasta IS NULL;

-- 3. Hacer las nuevas columnas NOT NULL después de migrar datos
ALTER TABLE programacion_menu 
ALTER COLUMN fecha_desde SET NOT NULL,
ALTER COLUMN fecha_hasta SET NOT NULL;

-- 4. Agregar constraint para validar que fecha_hasta >= fecha_desde
ALTER TABLE programacion_menu 
ADD CONSTRAINT check_fechas_rango 
CHECK (fecha_hasta >= fecha_desde);

-- 5. Crear índices para búsquedas por rango de fechas
CREATE INDEX IF NOT EXISTS idx_programacion_fecha_desde ON programacion_menu(fecha_desde);
CREATE INDEX IF NOT EXISTS idx_programacion_fecha_hasta ON programacion_menu(fecha_hasta);
CREATE INDEX IF NOT EXISTS idx_programacion_rango_fechas ON programacion_menu(fecha_desde, fecha_hasta);

-- 6. (Opcional) Eliminar la columna fecha antigua después de verificar que todo funciona
-- ALTER TABLE programacion_menu DROP COLUMN IF EXISTS fecha;

COMMENT ON COLUMN programacion_menu.fecha_desde IS 'Fecha de inicio del rango de programación';
COMMENT ON COLUMN programacion_menu.fecha_hasta IS 'Fecha de fin del rango de programación';
