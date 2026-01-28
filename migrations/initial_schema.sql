-- Schema inicial para ERP de Restaurantes
-- PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('persona', 'empresa')),
    ruc_ci VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    notas TEXT
);

CREATE INDEX idx_clientes_nombre ON clientes(nombre);
CREATE INDEX idx_clientes_ruc_ci ON clientes(ruc_ci);
CREATE INDEX idx_clientes_activo ON clientes(activo);

-- Tabla de proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    ruc VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    contacto_principal VARCHAR(200),
    dias_credito INTEGER DEFAULT 0 NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_proveedores_nombre ON proveedores(nombre);
CREATE INDEX idx_proveedores_ruc ON proveedores(ruc);
CREATE INDEX idx_proveedores_activo ON proveedores(activo);

-- Tabla de items (productos/insumos)
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(20) NOT NULL CHECK (categoria IN ('materia_prima', 'insumo', 'producto_terminado')),
    unidad VARCHAR(20) NOT NULL,
    calorias_por_unidad NUMERIC(10, 2),
    proveedor_autorizado_id INTEGER REFERENCES proveedores(id),
    tiempo_entrega_dias INTEGER DEFAULT 7 NOT NULL,
    costo_unitario_actual NUMERIC(10, 2),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_items_codigo ON items(codigo);
CREATE INDEX idx_items_nombre ON items(nombre);
CREATE INDEX idx_items_categoria ON items(categoria);
CREATE INDEX idx_items_proveedor ON items(proveedor_autorizado_id);

-- Tabla de inventario
CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE NOT NULL REFERENCES items(id),
    ubicacion VARCHAR(100) NOT NULL DEFAULT 'bodega_principal',
    cantidad_actual NUMERIC(10, 2) NOT NULL DEFAULT 0,
    cantidad_minima NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unidad VARCHAR(20) NOT NULL,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    ultimo_costo_unitario NUMERIC(10, 2)
);

CREATE INDEX idx_inventario_item ON inventario(item_id);
CREATE INDEX idx_inventario_ubicacion ON inventario(ubicacion);

-- Tabla de facturas
CREATE TABLE IF NOT EXISTS facturas (
    id SERIAL PRIMARY KEY,
    numero_factura VARCHAR(50) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cliente', 'proveedor')),
    cliente_id INTEGER REFERENCES clientes(id),
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
CREATE INDEX idx_facturas_cliente ON facturas(cliente_id);
CREATE INDEX idx_facturas_proveedor ON facturas(proveedor_id);
CREATE INDEX idx_facturas_estado ON facturas(estado);
CREATE INDEX idx_facturas_fecha ON facturas(fecha_recepcion);

-- Tabla de items de factura
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

-- Tabla de tickets
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
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

CREATE INDEX idx_tickets_cliente ON tickets(cliente_id);
CREATE INDEX idx_tickets_estado ON tickets(estado);
CREATE INDEX idx_tickets_asignado ON tickets(asignado_a);
CREATE INDEX idx_tickets_fecha ON tickets(fecha_creacion);

-- Tabla de recetas
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

-- Tabla de ingredientes de receta
CREATE TABLE IF NOT EXISTS receta_ingredientes (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    item_id INTEGER NOT NULL REFERENCES items(id),
    cantidad NUMERIC(10, 2) NOT NULL,
    unidad VARCHAR(20) NOT NULL
);

CREATE INDEX idx_receta_ingredientes_receta ON receta_ingredientes(receta_id);
CREATE INDEX idx_receta_ingredientes_item ON receta_ingredientes(item_id);

-- Tabla de programación de menús
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

-- Tabla de items de programación (recetas en el menú)
CREATE TABLE IF NOT EXISTS programacion_menu_items (
    id SERIAL PRIMARY KEY,
    programacion_id INTEGER NOT NULL REFERENCES programacion_menu(id) ON DELETE CASCADE,
    receta_id INTEGER NOT NULL REFERENCES recetas(id),
    cantidad_porciones INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_programacion_items_programacion ON programacion_menu_items(programacion_id);
CREATE INDEX idx_programacion_items_receta ON programacion_menu_items(receta_id);

-- Tabla de pedidos de compra
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

-- Tabla de items de pedido
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

-- Tabla de requerimientos (salidas de bodega)
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

-- Tabla de items de requerimiento
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

-- Tabla de cuentas contables (plan contable)
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

-- Comentarios en tablas
COMMENT ON TABLE clientes IS 'Base de datos central de clientes';
COMMENT ON TABLE proveedores IS 'Catálogo de proveedores';
COMMENT ON TABLE items IS 'Catálogo de productos/insumos';
COMMENT ON TABLE inventario IS 'Control de stock por item';
COMMENT ON TABLE facturas IS 'Facturas de clientes y proveedores';
COMMENT ON TABLE tickets IS 'Sistema de tickets/quejas de clientes';
COMMENT ON TABLE recetas IS 'Recetas de cocina';
COMMENT ON TABLE programacion_menu IS 'Programación de menús diarios';
COMMENT ON TABLE pedidos_compra IS 'Órdenes de compra a proveedores';
COMMENT ON TABLE requerimientos IS 'Salidas de bodega';
COMMENT ON TABLE cuentas_contables IS 'Plan contable jerárquico';
