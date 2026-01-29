-- ============================================================================
-- SCHEMA COMPLETO DE BASE DE DATOS - ERP RESTAURANTES
-- Sistema de gestión para cadena de restaurantes
-- PostgreSQL
-- ============================================================================
-- 
-- Este script crea todo el esquema de base de datos incluyendo:
-- - Tablas principales (Proveedores, Items, Labels, etc.)
-- - Relaciones entre tablas
-- - Índices para optimización
-- - Datos iniciales de labels internacionales
--
-- RELACIONES PRINCIPALES:
-- Proveedor -> Items (proveedor_autorizado_id)
-- Item -> Labels (tabla item_labels - muchos a muchos)
-- Esto permite saber qué alimentos provee cada proveedor y su clasificación
-- ============================================================================

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLA: PROVEEDORES
-- ============================================================================
-- Almacena información de proveedores que suministran alimentos/insumos
-- Relacionado con Items a través de proveedor_autorizado_id
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    ruc VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    nombre_contacto VARCHAR(200),  -- Nombre del contacto principal
    productos_que_provee TEXT,     -- Lista descriptiva de productos que provee
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_proveedores_nombre ON proveedores(nombre);
CREATE INDEX idx_proveedores_ruc ON proveedores(ruc);
CREATE INDEX idx_proveedores_activo ON proveedores(activo);

COMMENT ON TABLE proveedores IS 'Catálogo de proveedores que suministran alimentos e insumos';

-- ============================================================================
-- TABLA: ITEM_LABEL (Clasificaciones Internacionales de Alimentos)
-- ============================================================================
-- Clasificaciones internacionales basadas en FAO/WHO para categorizar alimentos
-- Permite clasificar items para generar recetas y menús
CREATE TABLE IF NOT EXISTS item_label (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,           -- Código internacional único
    nombre_es VARCHAR(200) NOT NULL,             -- Nombre en español
    nombre_en VARCHAR(200) NOT NULL,             -- Nombre en inglés
    descripcion TEXT,
    categoria_principal VARCHAR(100) NOT NULL,   -- Categoría principal (ej: Frutas y Verduras)
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_item_label_codigo ON item_label(codigo);
CREATE INDEX idx_item_label_categoria ON item_label(categoria_principal);
CREATE INDEX idx_item_label_activo ON item_label(activo);

COMMENT ON TABLE item_label IS 'Clasificaciones internacionales de alimentos (FAO/WHO) para categorizar items';

-- ============================================================================
-- TABLA: ITEMS (Productos/Insumos/Alimentos)
-- ============================================================================
-- Catálogo de productos, insumos y alimentos del sistema
-- RELACIÓN CON PROVEEDOR: proveedor_autorizado_id -> proveedores.id
-- RELACIÓN CON LABELS: tabla item_labels (muchos a muchos)
-- Esto permite saber qué proveedor provee qué alimentos y su clasificación
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('materia_prima', 'insumo', 'producto_terminado')),
    unidad VARCHAR(20) NOT NULL,                  -- kg, litro, unidad, etc.
    calorias_por_unidad NUMERIC(10, 2),
    proveedor_autorizado_id INTEGER REFERENCES proveedores(id) ON DELETE SET NULL,  -- RELACIÓN CON PROVEEDOR
    tiempo_entrega_dias INTEGER DEFAULT 7 NOT NULL,
    costo_unitario_actual NUMERIC(10, 2),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_items_codigo ON items(codigo);
CREATE INDEX idx_items_nombre ON items(nombre);
CREATE INDEX idx_items_categoria ON items(categoria);
CREATE INDEX idx_items_proveedor ON items(proveedor_autorizado_id);  -- Índice para búsqueda por proveedor
CREATE INDEX idx_items_activo ON items(activo);

COMMENT ON TABLE items IS 'Catálogo de productos, insumos y alimentos. Relacionado con proveedores y labels';

-- ============================================================================
-- TABLA: ITEM_LABELS (Relación Items - Labels)
-- ============================================================================
-- Relación muchos-a-muchos entre Items y Labels
-- Permite que un item tenga múltiples clasificaciones
-- Permite saber qué clasificaciones tiene cada alimento que provee un proveedor
CREATE TABLE IF NOT EXISTS item_labels (
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    label_id INTEGER NOT NULL REFERENCES item_label(id) ON DELETE CASCADE,
    PRIMARY KEY (item_id, label_id)
);

CREATE INDEX idx_item_labels_item ON item_labels(item_id);
CREATE INDEX idx_item_labels_label ON item_labels(label_id);

COMMENT ON TABLE item_labels IS 'Relación muchos-a-muchos: Items pueden tener múltiples clasificaciones (labels)';

-- ============================================================================
-- TABLA: INVENTARIO
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    ubicacion VARCHAR(100) NOT NULL DEFAULT 'bodega_principal',
    cantidad_actual NUMERIC(10, 2) NOT NULL DEFAULT 0,
    cantidad_minima NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unidad VARCHAR(20) NOT NULL,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ultimo_costo_unitario NUMERIC(10, 2)
);

CREATE INDEX idx_inventario_item ON inventario(item_id);
CREATE INDEX idx_inventario_ubicacion ON inventario(ubicacion);

COMMENT ON TABLE inventario IS 'Control de stock por item';

-- ============================================================================
-- TABLA: FACTURAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cliente', 'proveedor')),
    cliente_id INTEGER,  -- Puede ser NULL si se eliminó el módulo de clientes
    proveedor_id INTEGER REFERENCES proveedores(id),
    fecha_emision TIMESTAMP NOT NULL,
    fecha_recepcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    iva NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' NOT NULL CHECK (estado IN ('pendiente', 'parcial', 'aprobada', 'rechazada')),
    imagen_url VARCHAR(500),
    items_json JSONB,
    aprobado_por INTEGER,
    fecha_aprobacion TIMESTAMP,
    observaciones TEXT
);

CREATE INDEX idx_facturas_numero ON facturas(numero_factura);
CREATE INDEX idx_facturas_proveedor ON facturas(proveedor_id);
CREATE INDEX idx_facturas_estado ON facturas(estado);
CREATE INDEX idx_facturas_fecha ON facturas(fecha_recepcion);

COMMENT ON TABLE facturas IS 'Facturas de proveedores';

-- ============================================================================
-- TABLA: FACTURA_ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS factura_items (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id),
    cantidad_facturada NUMERIC(10, 2) NOT NULL,
    cantidad_aprobada NUMERIC(10, 2),
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    descripcion VARCHAR(500)
);

CREATE INDEX idx_factura_items_factura ON factura_items(factura_id);
CREATE INDEX idx_factura_items_item ON factura_items(item_id);

-- ============================================================================
-- TABLA: TICKETS
-- ============================================================================
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER,  -- Puede ser NULL si se eliminó el módulo de clientes
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('queja', 'consulta', 'sugerencia', 'reclamo')),
    asunto VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'abierto' NOT NULL CHECK (estado IN ('abierto', 'en_proceso', 'resuelto', 'cerrado')),
    prioridad VARCHAR(20) DEFAULT 'media' NOT NULL CHECK (prioridad IN ('baja', 'media', 'alta', 'urgente')),
    asignado_a INTEGER,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_resolucion TIMESTAMP,
    respuesta TEXT
);

CREATE INDEX idx_tickets_estado ON tickets(estado);
CREATE INDEX idx_tickets_asignado ON tickets(asignado_a);
CREATE INDEX idx_tickets_fecha ON tickets(fecha_creacion);

COMMENT ON TABLE tickets IS 'Sistema de tickets/quejas';

-- ============================================================================
-- TABLA: RECETAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS recetas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    porciones INTEGER NOT NULL DEFAULT 1,
    calorias_totales NUMERIC(10, 2),
    costo_total NUMERIC(10, 2),
    calorias_por_porcion NUMERIC(10, 2),
    costo_por_porcion NUMERIC(10, 2),
    tiempo_preparacion INTEGER,
    activa BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_recetas_nombre ON recetas(nombre);
CREATE INDEX idx_recetas_activa ON recetas(activa);

COMMENT ON TABLE recetas IS 'Recetas de cocina que usan items con sus clasificaciones';

-- ============================================================================
-- TABLA: RECETA_INGREDIENTES
-- ============================================================================
CREATE TABLE IF NOT EXISTS receta_ingredientes (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    cantidad NUMERIC(10, 2) NOT NULL,
    unidad VARCHAR(20) NOT NULL
);

CREATE INDEX idx_receta_ingredientes_receta ON receta_ingredientes(receta_id);
CREATE INDEX idx_receta_ingredientes_item ON receta_ingredientes(item_id);

-- ============================================================================
-- TABLA: PROGRAMACION_MENU
-- ============================================================================
CREATE TABLE IF NOT EXISTS programacion_menu (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tiempo_comida VARCHAR(20) NOT NULL CHECK (tiempo_comida IN ('desayuno', 'almuerzo', 'cena')),
    ubicacion VARCHAR(100) NOT NULL,
    personas_estimadas INTEGER NOT NULL DEFAULT 0,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_programacion_fecha ON programacion_menu(fecha);
CREATE INDEX idx_programacion_ubicacion ON programacion_menu(ubicacion);

COMMENT ON TABLE programacion_menu IS 'Programación de menús diarios';

-- ============================================================================
-- TABLA: PROGRAMACION_MENU_ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS programacion_menu_items (
    id SERIAL PRIMARY KEY,
    programacion_id INTEGER NOT NULL REFERENCES programacion_menu(id) ON DELETE CASCADE,
    receta_id INTEGER NOT NULL REFERENCES recetas(id),
    cantidad_porciones INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_programacion_items_programacion ON programacion_menu_items(programacion_id);
CREATE INDEX idx_programacion_items_receta ON programacion_menu_items(receta_id);

-- ============================================================================
-- TABLA: PEDIDOS_COMPRA
-- ============================================================================
CREATE TABLE IF NOT EXISTS pedidos_compra (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER NOT NULL REFERENCES proveedores(id),
    fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_entrega_esperada TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'borrador' NOT NULL CHECK (estado IN ('borrador', 'enviado', 'recibido', 'cancelado')),
    total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    creado_por INTEGER,
    observaciones TEXT
);

CREATE INDEX idx_pedidos_proveedor ON pedidos_compra(proveedor_id);
CREATE INDEX idx_pedidos_estado ON pedidos_compra(estado);
CREATE INDEX idx_pedidos_fecha ON pedidos_compra(fecha_pedido);

COMMENT ON TABLE pedidos_compra IS 'Órdenes de compra a proveedores';

-- ============================================================================
-- TABLA: PEDIDO_COMPRA_ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS pedido_compra_items (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos_compra(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    cantidad NUMERIC(10, 2) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL
);

CREATE INDEX idx_pedido_items_pedido ON pedido_compra_items(pedido_id);
CREATE INDEX idx_pedido_items_item ON pedido_compra_items(item_id);

-- ============================================================================
-- TABLA: REQUERIMIENTOS
-- ============================================================================
CREATE TABLE IF NOT EXISTS requerimientos (
    id SERIAL PRIMARY KEY,
    solicitante INTEGER NOT NULL,
    receptor INTEGER NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' NOT NULL CHECK (estado IN ('pendiente', 'entregado', 'cancelado')),
    observaciones VARCHAR(500)
);

CREATE INDEX idx_requerimientos_estado ON requerimientos(estado);
CREATE INDEX idx_requerimientos_fecha ON requerimientos(fecha);

COMMENT ON TABLE requerimientos IS 'Salidas de bodega';

-- ============================================================================
-- TABLA: REQUERIMIENTO_ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS requerimiento_items (
    id SERIAL PRIMARY KEY,
    requerimiento_id INTEGER NOT NULL REFERENCES requerimientos(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    cantidad_solicitada NUMERIC(10, 2) NOT NULL,
    cantidad_entregada NUMERIC(10, 2),
    hora_entrega TIME
);

CREATE INDEX idx_requerimiento_items_requerimiento ON requerimiento_items(requerimiento_id);
CREATE INDEX idx_requerimiento_items_item ON requerimiento_items(item_id);

-- ============================================================================
-- TABLA: CUENTAS_CONTABLES
-- ============================================================================
CREATE TABLE IF NOT EXISTS cuentas_contables (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('activo', 'pasivo', 'ingreso', 'gasto')),
    padre_id INTEGER REFERENCES cuentas_contables(id),
    descripcion TEXT
);

CREATE INDEX idx_cuentas_codigo ON cuentas_contables(codigo);
CREATE INDEX idx_cuentas_tipo ON cuentas_contables(tipo);
CREATE INDEX idx_cuentas_padre ON cuentas_contables(padre_id);

COMMENT ON TABLE cuentas_contables IS 'Plan contable jerárquico';

-- ============================================================================
-- TABLA: CHAROLAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS charolas (
    id SERIAL PRIMARY KEY,
    numero_charola VARCHAR(50) UNIQUE NOT NULL,
    fecha_servicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ubicacion VARCHAR(100) NOT NULL,
    tiempo_comida VARCHAR(50) NOT NULL CHECK (tiempo_comida IN ('desayuno', 'almuerzo', 'cena')),
    personas_servidas INTEGER NOT NULL DEFAULT 0,
    total_ventas NUMERIC(10, 2) NOT NULL DEFAULT 0,
    costo_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ganancia NUMERIC(10, 2) NOT NULL DEFAULT 0,
    observaciones TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_charolas_fecha ON charolas(fecha_servicio);
CREATE INDEX idx_charolas_ubicacion ON charolas(ubicacion);
CREATE INDEX idx_charolas_numero ON charolas(numero_charola);

COMMENT ON TABLE charolas IS 'Registro de charolas/platos servidos';

-- ============================================================================
-- TABLA: CHAROLA_ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS charola_items (
    id SERIAL PRIMARY KEY,
    charola_id INTEGER NOT NULL REFERENCES charolas(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id),
    receta_id INTEGER REFERENCES recetas(id),
    nombre_item VARCHAR(200) NOT NULL,
    cantidad NUMERIC(10, 2) NOT NULL,
    precio_unitario NUMERIC(10, 2) NOT NULL,
    costo_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    costo_subtotal NUMERIC(10, 2) NOT NULL
);

CREATE INDEX idx_charola_items_charola ON charola_items(charola_id);
CREATE INDEX idx_charola_items_item ON charola_items(item_id);
CREATE INDEX idx_charola_items_receta ON charola_items(receta_id);

-- ============================================================================
-- TABLA: MERMAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS mermas (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id),
    fecha_merma TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('vencimiento', 'deterioro', 'preparacion', 'servicio', 'otro')),
    cantidad NUMERIC(10, 2) NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    costo_unitario NUMERIC(10, 2) NOT NULL,
    costo_total NUMERIC(10, 2) NOT NULL,
    motivo TEXT,
    ubicacion VARCHAR(100),
    registrado_por INTEGER,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_mermas_fecha ON mermas(fecha_merma);
CREATE INDEX idx_mermas_item ON mermas(item_id);
CREATE INDEX idx_mermas_tipo ON mermas(tipo);

COMMENT ON TABLE mermas IS 'Registro de mermas/pérdidas de inventario';

-- ============================================================================
-- TABLA: CONVERSACIONES (Chat AI)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversaciones (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200),
    usuario_id INTEGER,
    contexto_modulo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    activa BOOLEAN DEFAULT TRUE NOT NULL
);

CREATE INDEX idx_conversaciones_fecha ON conversaciones(fecha_creacion);
CREATE INDEX idx_conversaciones_usuario ON conversaciones(usuario_id);
CREATE INDEX idx_conversaciones_activa ON conversaciones(activa);

COMMENT ON TABLE conversaciones IS 'Conversaciones del módulo Chat AI';

-- ============================================================================
-- TABLA: MENSAJES (Chat AI)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mensajes (
    id SERIAL PRIMARY KEY,
    conversacion_id INTEGER NOT NULL REFERENCES conversaciones(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('usuario', 'asistente', 'sistema')),
    contenido TEXT NOT NULL,
    tokens_usados INTEGER,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_mensajes_conversacion ON mensajes(conversacion_id);
CREATE INDEX idx_mensajes_fecha ON mensajes(fecha_envio);
CREATE INDEX idx_mensajes_tipo ON mensajes(tipo);

COMMENT ON TABLE mensajes IS 'Mensajes de las conversaciones del Chat AI';

-- ============================================================================
-- DATOS INICIALES: LABELS INTERNACIONALES DE ALIMENTOS
-- ============================================================================
-- Clasificaciones basadas en estándares FAO/WHO para categorizar alimentos
-- Estos labels permiten clasificar items y generar recetas/menús

INSERT INTO item_label (codigo, nombre_es, nombre_en, categoria_principal, descripcion) VALUES
-- FRUTAS Y VERDURAS
('FRU_FRESH', 'Frutas Frescas', 'Fresh Fruits', 'Frutas y Verduras', 'Frutas frescas de temporada'),
('FRU_DRIED', 'Frutas Secas', 'Dried Fruits', 'Frutas y Verduras', 'Frutas deshidratadas'),
('VEG_LEAFY', 'Verduras de Hoja', 'Leafy Vegetables', 'Frutas y Verduras', 'Espinacas, lechuga, acelgas, etc.'),
('VEG_ROOT', 'Verduras de Raíz', 'Root Vegetables', 'Frutas y Verduras', 'Zanahorias, papas, remolachas, etc.'),
('VEG_CRUCIFEROUS', 'Verduras Crucíferas', 'Cruciferous Vegetables', 'Frutas y Verduras', 'Brócoli, coliflor, repollo, etc.'),
('VEG_NIGHTSHADE', 'Solanáceas', 'Nightshades', 'Frutas y Verduras', 'Tomates, pimientos, berenjenas, etc.'),

-- CEREALES Y GRANOS
('GRAIN_WHEAT', 'Trigo', 'Wheat', 'Cereales y Granos', 'Trigo y derivados'),
('GRAIN_RICE', 'Arroz', 'Rice', 'Cereales y Granos', 'Arroz blanco, integral, salvaje'),
('GRAIN_CORN', 'Maíz', 'Corn', 'Cereales y Granos', 'Maíz y derivados'),
('GRAIN_OATS', 'Avena', 'Oats', 'Cereales y Granos', 'Avena y productos de avena'),
('GRAIN_QUINOA', 'Quinoa', 'Quinoa', 'Cereales y Granos', 'Quinoa y pseudocereales'),
('GRAIN_LEGUMES', 'Legumbres', 'Legumes', 'Cereales y Granos', 'Frijoles, lentejas, garbanzos, etc.'),

-- PROTEÍNAS
('PROT_BEEF', 'Carne de Res', 'Beef', 'Proteínas', 'Carne de res y ternera'),
('PROT_PORK', 'Cerdo', 'Pork', 'Proteínas', 'Carne de cerdo'),
('PROT_POULTRY', 'Aves', 'Poultry', 'Proteínas', 'Pollo, pavo, pato, etc.'),
('PROT_FISH', 'Pescado', 'Fish', 'Proteínas', 'Pescados frescos'),
('PROT_SEAFOOD', 'Mariscos', 'Seafood', 'Proteínas', 'Camarones, langostinos, pulpo, etc.'),
('PROT_EGGS', 'Huevos', 'Eggs', 'Proteínas', 'Huevos de gallina y otras aves'),
('PROT_PLANT', 'Proteína Vegetal', 'Plant Protein', 'Proteínas', 'Tofu, tempeh, seitán, etc.'),

-- LÁCTEOS
('DAIRY_MILK', 'Leche', 'Milk', 'Lácteos', 'Leche de vaca, cabra, etc.'),
('DAIRY_CHEESE', 'Queso', 'Cheese', 'Lácteos', 'Quesos diversos'),
('DAIRY_YOGURT', 'Yogurt', 'Yogurt', 'Lácteos', 'Yogurt natural y saborizado'),
('DAIRY_CREAM', 'Crema', 'Cream', 'Lácteos', 'Crema de leche, nata'),
('DAIRY_BUTTER', 'Mantequilla', 'Butter', 'Lácteos', 'Mantequilla y margarina'),

-- GRASAS Y ACEITES
('FAT_OIL_OLIVE', 'Aceite de Oliva', 'Olive Oil', 'Grasas y Aceites', 'Aceite de oliva extra virgen y refinado'),
('FAT_OIL_VEGETABLE', 'Aceite Vegetal', 'Vegetable Oil', 'Grasas y Aceites', 'Aceites vegetales diversos'),
('FAT_NUTS', 'Frutos Secos', 'Nuts', 'Grasas y Aceites', 'Almendras, nueces, avellanas, etc.'),
('FAT_SEEDS', 'Semillas', 'Seeds', 'Grasas y Aceites', 'Semillas de girasol, chía, sésamo, etc.'),

-- ESPECIAS Y CONDIMENTOS
('SPICE_SALT', 'Sal', 'Salt', 'Especias y Condimentos', 'Sal de mesa y sales especiales'),
('SPICE_PEPPER', 'Pimienta', 'Pepper', 'Especias y Condimentos', 'Pimienta negra, blanca, rosa'),
('SPICE_HERBS', 'Hierbas', 'Herbs', 'Especias y Condimentos', 'Albahaca, orégano, romero, etc.'),
('SPICE_SPICES', 'Especias', 'Spices', 'Especias y Condimentos', 'Canela, clavo, comino, etc.'),
('SPICE_GARLIC', 'Ajo', 'Garlic', 'Especias y Condimentos', 'Ajo fresco y en polvo'),
('SPICE_ONION', 'Cebolla', 'Onion', 'Especias y Condimentos', 'Cebolla blanca, morada, verde'),

-- BEBIDAS
('BEV_WATER', 'Agua', 'Water', 'Bebidas', 'Agua natural y mineral'),
('BEV_JUICE', 'Jugos', 'Juice', 'Bebidas', 'Jugos naturales y procesados'),
('BEV_SOFT', 'Refrescos', 'Soft Drinks', 'Bebidas', 'Bebidas gaseosas'),
('BEV_ALCOHOL', 'Alcohol', 'Alcohol', 'Bebidas', 'Vino, cerveza, licores'),
('BEV_TEA', 'Té', 'Tea', 'Bebidas', 'Té verde, negro, herbal'),
('BEV_COFFEE', 'Café', 'Coffee', 'Bebidas', 'Café molido, granos, instantáneo'),

-- OTROS
('OTHER_SUGAR', 'Azúcar', 'Sugar', 'Otros', 'Azúcar blanco, moreno, miel'),
('OTHER_VINEGAR', 'Vinagre', 'Vinegar', 'Otros', 'Vinagre de vino, manzana, balsámico'),
('OTHER_FLOUR', 'Harina', 'Flour', 'Otros', 'Harinas diversas'),
('OTHER_PASTA', 'Pasta', 'Pasta', 'Otros', 'Pastas secas y frescas'),
('OTHER_BREAD', 'Pan', 'Bread', 'Otros', 'Pan blanco, integral, artesanal')
ON CONFLICT (codigo) DO NOTHING;

-- ============================================================================
-- VISTAS ÚTILES PARA CONSULTAS
-- ============================================================================

-- Vista: Proveedores con sus Items y Clasificaciones
CREATE OR REPLACE VIEW v_proveedores_items_labels AS
SELECT 
    p.id AS proveedor_id,
    p.nombre AS proveedor_nombre,
    p.ruc AS proveedor_ruc,
    i.id AS item_id,
    i.codigo AS item_codigo,
    i.nombre AS item_nombre,
    i.categoria AS item_categoria,
    il.id AS label_id,
    il.codigo AS label_codigo,
    il.nombre_es AS label_nombre_es,
    il.categoria_principal AS label_categoria
FROM proveedores p
LEFT JOIN items i ON i.proveedor_autorizado_id = p.id
LEFT JOIN item_labels il_rel ON il_rel.item_id = i.id
LEFT JOIN item_label il ON il.id = il_rel.label_id
WHERE p.activo = TRUE AND (i.activo = TRUE OR i.id IS NULL)
ORDER BY p.nombre, i.nombre, il.categoria_principal, il.nombre_es;

COMMENT ON VIEW v_proveedores_items_labels IS 'Vista que muestra qué alimentos provee cada proveedor y sus clasificaciones';

-- Vista: Items con sus Labels agrupados
CREATE OR REPLACE VIEW v_items_labels AS
SELECT 
    i.id AS item_id,
    i.codigo AS item_codigo,
    i.nombre AS item_nombre,
    i.categoria AS item_categoria,
    p.nombre AS proveedor_nombre,
    STRING_AGG(il.nombre_es, ', ' ORDER BY il.categoria_principal, il.nombre_es) AS labels
FROM items i
LEFT JOIN proveedores p ON p.id = i.proveedor_autorizado_id
LEFT JOIN item_labels il_rel ON il_rel.item_id = i.id
LEFT JOIN item_label il ON il.id = il_rel.label_id AND il.activo = TRUE
WHERE i.activo = TRUE
GROUP BY i.id, i.codigo, i.nombre, i.categoria, p.nombre
ORDER BY i.nombre;

COMMENT ON VIEW v_items_labels IS 'Vista que muestra items con sus labels agrupados como texto';

-- ============================================================================
-- FIN DEL SCHEMA
-- ============================================================================
-- 
-- RELACIONES CLAVE:
-- 1. Proveedor -> Items (proveedor_autorizado_id)
-- 2. Item -> Labels (tabla item_labels)
-- 3. Esto permite consultar: qué alimentos provee cada proveedor y su clasificación
--
-- CONSULTAS ÚTILES:
-- - Ver todos los items de un proveedor: SELECT * FROM items WHERE proveedor_autorizado_id = X
-- - Ver clasificaciones de un item: SELECT il.* FROM item_label il JOIN item_labels il_rel ON il.id = il_rel.label_id WHERE il_rel.item_id = X
-- - Ver qué proveedor provee qué clasificaciones: SELECT * FROM v_proveedores_items_labels WHERE label_codigo = 'PROT_FISH'
-- ============================================================================
