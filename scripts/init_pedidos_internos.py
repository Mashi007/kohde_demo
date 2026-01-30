"""
Script para inicializar pedidos internos de prueba.
Requiere: Items activos
"""
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.item import Item
from models.pedido_interno import PedidoInterno, PedidoInternoItem, EstadoPedidoInterno

def init_pedidos_internos():
    """Inicializa 10 pedidos internos variados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE PEDIDOS INTERNOS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    print("\n2. INICIALIZANDO PEDIDOS INTERNOS...")
    
    estados = [EstadoPedidoInterno.PENDIENTE, EstadoPedidoInterno.ENTREGADO, EstadoPedidoInterno.CANCELADO]
    ubicaciones = ['restaurante_A', 'restaurante_B', 'cocina_central']
    responsables_bodega = [
        {'id': 1, 'nombre': 'Carlos Mendoza'},
        {'id': 2, 'nombre': 'Ana López'},
        {'id': 3, 'nombre': 'Roberto Silva'}
    ]
    responsables_cocina = [
        {'id': 4, 'nombre': 'María González'},
        {'id': 5, 'nombre': 'Juan Pérez'},
        {'id': 6, 'nombre': 'Laura Martínez'}
    ]
    
    pedidos_data = []
    fecha_base = datetime.now() - timedelta(days=15)
    
    for i in range(10):
        estado = choice(estados)
        fecha_pedido = fecha_base + timedelta(days=randint(0, 12))
        fecha_entrega = None
        
        responsable_bodega = choice(responsables_bodega)
        responsable_cocina = None
        
        if estado == EstadoPedidoInterno.ENTREGADO:
            fecha_entrega = fecha_pedido + timedelta(hours=randint(2, 8))
            responsable_cocina = choice(responsables_cocina)
        
        # Seleccionar 3-6 items aleatorios
        items_pedido = []
        items_seleccionados = []
        num_items = randint(3, 6)
        
        for _ in range(num_items):
            item = choice(items)
            if item.id not in items_seleccionados:
                items_seleccionados.append(item.id)
                cantidad = Decimal(str(round(uniform(5, 50), 2)))
                
                items_pedido.append({
                    'item_id': item.id,
                    'cantidad': cantidad,
                    'unidad': item.unidad
                })
        
        pedidos_data.append({
            'fecha_pedido': fecha_pedido,
            'fecha_entrega': fecha_entrega,
            'estado': estado,
            'entregado_por_id': responsable_bodega['id'],
            'entregado_por_nombre': responsable_bodega['nombre'],
            'recibido_por_id': responsable_cocina['id'] if responsable_cocina else None,
            'recibido_por_nombre': responsable_cocina['nombre'] if responsable_cocina else None,
            'ubicacion': choice(ubicaciones),
            'observaciones': f"Pedido interno #{i+1} - Transferencia bodega a cocina",
            'items': items_pedido
        })
    
    pedidos_creados = []
    for pedido_data in pedidos_data:
        items_data = pedido_data.pop('items')
        ubicacion = pedido_data.pop('ubicacion')
        
        # Verificar si ya existe
        existing = PedidoInterno.query.filter_by(
            fecha_pedido=pedido_data['fecha_pedido'],
            entregado_por_id=pedido_data['entregado_por_id']
        ).first()
        
        if not existing:
            pedido = PedidoInterno(**pedido_data)
            db.session.add(pedido)
            db.session.flush()
            
            # Crear items del pedido
            for item_data in items_data:
                pedido_item = PedidoInternoItem(
                    pedido_id=pedido.id,
                    **item_data
                )
                db.session.add(pedido_item)
            
            pedidos_creados.append(pedido)
            print(f"  ✓ Creado pedido interno #{pedido.id} - {pedido.estado.value} - {len(items_data)} items")
        else:
            pedidos_creados.append(existing)
            print(f"  ↻ Ya existe pedido interno del {pedido_data['fecha_pedido'].date()}")
    
    db.session.commit()
    print(f"\n✓ Total pedidos internos creados/actualizados: {len(pedidos_creados)}")
    return pedidos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        pedidos = init_pedidos_internos()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(pedidos)} pedidos internos disponibles")
        print(f"{'='*60}")
