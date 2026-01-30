"""simplificar_enums_y_agregar_indices

Revision ID: 39df3de8b2c0
Revises: 
Create Date: 2026-01-30 09:06:10.138024

Esta migración:
1. Cambia el enum estadopedido a VARCHAR simple (más práctico)
2. Agrega índices para mejorar el rendimiento de consultas
3. Agrega CheckConstraint para validación de estados
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '39df3de8b2c0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cambiar enum estadopedido a VARCHAR simple
    # Primero verificar si existe el enum y la columna
    op.execute("""
        DO $$ 
        BEGIN
            -- Cambiar la columna de enum a VARCHAR si existe
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'pedidos_compra' 
                AND column_name = 'estado'
            ) THEN
                -- Convertir valores existentes de enum a strings minúsculas
                ALTER TABLE pedidos_compra 
                ALTER COLUMN estado TYPE VARCHAR(20) 
                USING LOWER(estado::text);
                
                -- Agregar CheckConstraint para validación
                ALTER TABLE pedidos_compra
                ADD CONSTRAINT check_estado_pedido_valido 
                CHECK (estado IN ('borrador', 'enviado', 'recibido', 'cancelado'));
            END IF;
        END $$;
    """)
    
    # 2. Agregar índices para mejorar consultas frecuentes
    
    # Índices en pedidos_compra (consultas por estado y fecha)
    op.create_index(
        'ix_pedidos_compra_estado',
        'pedidos_compra',
        ['estado'],
        unique=False
    )
    op.create_index(
        'ix_pedidos_compra_fecha_pedido',
        'pedidos_compra',
        ['fecha_pedido'],
        unique=False
    )
    op.create_index(
        'ix_pedidos_compra_proveedor_id',
        'pedidos_compra',
        ['proveedor_id'],
        unique=False
    )
    op.create_index(
        'ix_pedidos_compra_estado_fecha',
        'pedidos_compra',
        ['estado', 'fecha_pedido'],
        unique=False
    )
    
    # Índices en facturas (consultas por estado y fecha)
    op.create_index(
        'ix_facturas_estado',
        'facturas',
        ['estado'],
        unique=False
    )
    op.create_index(
        'ix_facturas_fecha_recepcion',
        'facturas',
        ['fecha_recepcion'],
        unique=False
    )
    op.create_index(
        'ix_facturas_proveedor_id',
        'facturas',
        ['proveedor_id'],
        unique=False
    )
    op.create_index(
        'ix_facturas_estado_fecha',
        'facturas',
        ['estado', 'fecha_recepcion'],
        unique=False
    )
    
    # Índices en inventario (consultas por item_id y ubicacion)
    op.create_index(
        'ix_inventario_item_id',
        'inventario',
        ['item_id'],
        unique=False
    )
    op.create_index(
        'ix_inventario_ubicacion',
        'inventario',
        ['ubicacion'],
        unique=False
    )
    
    # Índices en items (consultas por codigo, activo, categoria)
    op.create_index(
        'ix_items_codigo',
        'items',
        ['codigo'],
        unique=False
    )
    op.create_index(
        'ix_items_activo',
        'items',
        ['activo'],
        unique=False
    )
    op.create_index(
        'ix_items_categoria',
        'items',
        ['categoria'],
        unique=False
    )
    op.create_index(
        'ix_items_proveedor_autorizado',
        'items',
        ['proveedor_autorizado_id'],
        unique=False
    )
    
    # Índices en proveedores (consultas por nombre y activo)
    op.create_index(
        'ix_proveedores_nombre',
        'proveedores',
        ['nombre'],
        unique=False
    )
    op.create_index(
        'ix_proveedores_activo',
        'proveedores',
        ['activo'],
        unique=False
    )
    
    # Índices en recetas (consultas por activa y tipo)
    op.create_index(
        'ix_recetas_activa',
        'recetas',
        ['activa'],
        unique=False
    )
    op.create_index(
        'ix_recetas_tipo',
        'recetas',
        ['tipo'],
        unique=False
    )
    
    # Índices en programacion_menu (consultas por fecha y ubicacion)
    op.create_index(
        'ix_programacion_menu_fecha',
        'programacion_menu',
        ['fecha'],
        unique=False
    )
    op.create_index(
        'ix_programacion_menu_ubicacion',
        'programacion_menu',
        ['ubicacion'],
        unique=False
    )
    op.create_index(
        'ix_programacion_menu_fecha_ubicacion',
        'programacion_menu',
        ['fecha', 'ubicacion'],
        unique=False
    )
    
    # Índices en charolas (consultas por fecha_servicio)
    op.create_index(
        'ix_charolas_fecha_servicio',
        'charolas',
        ['fecha_servicio'],
        unique=False
    )
    op.create_index(
        'ix_charolas_ubicacion',
        'charolas',
        ['ubicacion'],
        unique=False
    )
    
    # Índices en mermas (consultas por fecha_merma e item_id)
    op.create_index(
        'ix_mermas_fecha_merma',
        'mermas',
        ['fecha_merma'],
        unique=False
    )
    op.create_index(
        'ix_mermas_item_id',
        'mermas',
        ['item_id'],
        unique=False
    )
    
    # Índices en conversaciones (consultas por activa y fecha)
    op.create_index(
        'ix_conversaciones_activa',
        'conversaciones',
        ['activa'],
        unique=False
    )
    op.create_index(
        'ix_conversaciones_fecha_actualizacion',
        'conversaciones',
        ['fecha_actualizacion'],
        unique=False
    )
    
    # Índices en mensajes (consultas por conversacion_id)
    op.create_index(
        'ix_mensajes_conversacion_id',
        'mensajes',
        ['conversacion_id'],
        unique=False
    )
    op.create_index(
        'ix_mensajes_fecha_envio',
        'mensajes',
        ['fecha_envio'],
        unique=False
    )


def downgrade() -> None:
    # Eliminar índices (en orden inverso)
    op.drop_index('ix_mensajes_fecha_envio', table_name='mensajes')
    op.drop_index('ix_mensajes_conversacion_id', table_name='mensajes')
    op.drop_index('ix_conversaciones_fecha_actualizacion', table_name='conversaciones')
    op.drop_index('ix_conversaciones_activa', table_name='conversaciones')
    op.drop_index('ix_mermas_item_id', table_name='mermas')
    op.drop_index('ix_mermas_fecha_merma', table_name='mermas')
    op.drop_index('ix_charolas_ubicacion', table_name='charolas')
    op.drop_index('ix_charolas_fecha_servicio', table_name='charolas')
    op.drop_index('ix_programacion_menu_fecha_ubicacion', table_name='programacion_menu')
    op.drop_index('ix_programacion_menu_ubicacion', table_name='programacion_menu')
    op.drop_index('ix_programacion_menu_fecha', table_name='programacion_menu')
    op.drop_index('ix_recetas_tipo', table_name='recetas')
    op.drop_index('ix_recetas_activa', table_name='recetas')
    op.drop_index('ix_proveedores_activo', table_name='proveedores')
    op.drop_index('ix_proveedores_nombre', table_name='proveedores')
    op.drop_index('ix_items_proveedor_autorizado', table_name='items')
    op.drop_index('ix_items_categoria', table_name='items')
    op.drop_index('ix_items_activo', table_name='items')
    op.drop_index('ix_items_codigo', table_name='items')
    op.drop_index('ix_inventario_ubicacion', table_name='inventario')
    op.drop_index('ix_inventario_item_id', table_name='inventario')
    op.drop_index('ix_facturas_estado_fecha', table_name='facturas')
    op.drop_index('ix_facturas_proveedor_id', table_name='facturas')
    op.drop_index('ix_facturas_fecha_recepcion', table_name='facturas')
    op.drop_index('ix_facturas_estado', table_name='facturas')
    op.drop_index('ix_pedidos_compra_estado_fecha', table_name='pedidos_compra')
    op.drop_index('ix_pedidos_compra_proveedor_id', table_name='pedidos_compra')
    op.drop_index('ix_pedidos_compra_fecha_pedido', table_name='pedidos_compra')
    op.drop_index('ix_pedidos_compra_estado', table_name='pedidos_compra')
    
    # Eliminar CheckConstraint
    op.execute("ALTER TABLE pedidos_compra DROP CONSTRAINT IF EXISTS check_estado_pedido_valido;")
    
    # Revertir a enum (si es necesario, pero mejor dejar como VARCHAR)
    # Nota: No revertimos el enum porque es más práctico mantenerlo como VARCHAR
