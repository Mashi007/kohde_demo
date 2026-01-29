-- Migración: Agregar sistema de labels/clasificaciones internacionales para Items

-- Tabla de labels/clasificaciones internacionales
CREATE TABLE IF NOT EXISTS item_label (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre_es VARCHAR(200) NOT NULL,
    nombre_en VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_principal VARCHAR(100) NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Tabla de relación muchos-a-muchos entre Items y Labels
CREATE TABLE IF NOT EXISTS item_labels (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    label_id INTEGER NOT NULL REFERENCES item_label(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, label_id)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_item_label_codigo ON item_label(codigo);
CREATE INDEX IF NOT EXISTS idx_item_label_categoria ON item_label(categoria_principal);
CREATE INDEX IF NOT EXISTS idx_item_labels_item ON item_labels(item_id);
CREATE INDEX IF NOT EXISTS idx_item_labels_label ON item_labels(label_id);
