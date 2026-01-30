-- ============================================================================
-- TABLA: CONVERSACIONES_CONTACTOS (CRM)
-- ============================================================================
-- Historial de conversaciones por email y WhatsApp con contactos
-- Permite mantener un registro completo de todas las comunicaciones
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversaciones_contactos (
    id SERIAL PRIMARY KEY,
    contacto_id INTEGER NOT NULL REFERENCES contactos(id) ON DELETE CASCADE,
    tipo_mensaje VARCHAR(20) NOT NULL CHECK (tipo_mensaje IN ('email', 'whatsapp')),
    direccion VARCHAR(20) NOT NULL CHECK (direccion IN ('enviado', 'recibido')) DEFAULT 'enviado',
    asunto VARCHAR(500),  -- Solo para emails
    contenido TEXT NOT NULL,
    mensaje_id_externo VARCHAR(200),  -- ID del mensaje en WhatsApp/Email service
    estado VARCHAR(50) DEFAULT 'enviado',  -- enviado, entregado, leido, error
    error TEXT,  -- Mensaje de error si falló
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Índices para optimización
CREATE INDEX idx_conversaciones_contacto ON conversaciones_contactos(contacto_id);
CREATE INDEX idx_conversaciones_tipo ON conversaciones_contactos(tipo_mensaje);
CREATE INDEX idx_conversaciones_fecha ON conversaciones_contactos(fecha_envio DESC);
CREATE INDEX idx_conversaciones_estado ON conversaciones_contactos(estado);

COMMENT ON TABLE conversaciones_contactos IS 'Historial de conversaciones por email y WhatsApp con contactos';
COMMENT ON COLUMN conversaciones_contactos.tipo_mensaje IS 'Tipo de mensaje: email o whatsapp';
COMMENT ON COLUMN conversaciones_contactos.direccion IS 'Dirección: enviado (por nosotros) o recibido';
COMMENT ON COLUMN conversaciones_contactos.mensaje_id_externo IS 'ID del mensaje en el servicio externo (WhatsApp/Email)';
