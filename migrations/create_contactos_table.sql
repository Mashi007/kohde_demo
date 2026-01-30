-- ============================================================================
-- TABLA: CONTACTOS (CRM)
-- ============================================================================
-- Almacena contactos de proveedores o colaboradores con capacidad de conversación
-- Permite gestionar comunicaciones por email y WhatsApp
-- ============================================================================

CREATE TABLE IF NOT EXISTS contactos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    whatsapp VARCHAR(20),  -- Número de WhatsApp
    telefono VARCHAR(20),
    proyecto VARCHAR(200),  -- Proyecto asociado
    cargo VARCHAR(100),  -- Cargo/posición
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('proveedor', 'colaborador')) DEFAULT 'proveedor',
    proveedor_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL,
    notas TEXT,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para optimización
CREATE INDEX idx_contactos_nombre ON contactos(nombre);
CREATE INDEX idx_contactos_email ON contactos(email);
CREATE INDEX idx_contactos_tipo ON contactos(tipo);
CREATE INDEX idx_contactos_proveedor ON contactos(proveedor_id);
CREATE INDEX idx_contactos_activo ON contactos(activo);
CREATE INDEX idx_contactos_proyecto ON contactos(proyecto);

COMMENT ON TABLE contactos IS 'Contactos de proveedores o colaboradores con capacidad de conversación por email y WhatsApp';
COMMENT ON COLUMN contactos.tipo IS 'Tipo de contacto: proveedor o colaborador';
COMMENT ON COLUMN contactos.proyecto IS 'Proyecto asociado al contacto';
COMMENT ON COLUMN contactos.cargo IS 'Cargo o posición del contacto';
