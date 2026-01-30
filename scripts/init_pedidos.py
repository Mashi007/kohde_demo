"""
Script para inicializar pedidos de compra de prueba.
Requiere: Proveedores e Items activos
"""
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.proveedor import Proveedor
from models.item import Item
from models.pedido import PedidoCompra, PedidoCompraItem, EstadoPedido

def init_pedidos():
    """Inicializa 10 pedidos de compra variados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE PEDIDOS DE COMPRA")
    print("=" * 60)
    
    # Verificar proveedores
    proveedores = Proveedor.query.filter_by(activo=True).all()
    if not proveedores:
        print("\n❌ Error: No hay proveedores activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(proveedores)} proveedores activos")
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"✓ Encontrados {len(items)} items activos")
    
    print("\n2. INICIALIZANDO PEDIDOS...")
    
    estados = [EstadoPedido.BORRADOR, EstadoPedido.ENVIADO, EstadoPedido.RECIBIDO, EstadoPedido.CANCELADO]
    
    pedidos_data = []
    fecha_base = datetime.now() - timedelta(days=30)
    
    for i in range(10):
        proveedor = choice(proveedores)
        estado = choice(estados)
        fecha_pedido = fecha_base + timedelta(days=randint(0, 25))
        
        # Fecha de entrega esperada: 2-7 días después del pedido
        fecha_entrega_esperada = None
        if estado != EstadoPedido.CANCELADO:
            fecha_entrega_esperada = fecha_pedido + timedelta(days=randint(2, 7))
        
        # Seleccionar 2-5 items aleatorios para este pedido
        items_pedido = []
        items_seleccionados = []
        num_items = randint(2, 5)
        
        for _ in range(num_items):
            item = choice(items)
            if item.id not in items_seleccionados:
                items_seleccionados.append(item.id)
                cantidad = Decimal(str(round(uniform(10, 100), 2)))
                precio_unitario = item.costo_unitario_actual or Decimal(str(round(uniform(1, 10), 2)))
                subtotal = cantidad * precio_unitario
                
                items_pedido.append({
                    'item_id': item.id,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                })
        
        total = sum(item['subtotal'] for item in items_pedido)
        
        pedidos_data.append({
            'proveedor_id': proveedor.id,
            'fecha_pedido': fecha_pedido,
            'fecha_entrega_esperada': fecha_entrega_esperada,
            'estado': estado,
            'total': total,
            'creado_por': 1,  # usuario_id por defecto
            'observaciones': f"Pedido {i+1} - {proveedor.nombre}",
            'items': items_pedido
        })
    
    pedidos_creados = []
    for pedido_data in pedidos_data:
        items_data = pedido_data.pop('items')
        
        # Verificar si ya existe un pedido similar
        existing = PedidoCompra.query.filter_by(
            proveedor_id=pedido_data['proveedor_id'],
            fecha_pedido=pedido_data['fecha_pedido']
        ).first()
        
        if not existing:
            pedido = PedidoCompra(**pedido_data)
            db.session.add(pedido)
            db.session.flush()  # Para obtener el ID
            
            # Crear items del pedido
            for item_data in items_data:
                pedido_item = PedidoCompraItem(
                    pedido_id=pedido.id,
                    **item_data
                )
                db.session.add(pedido_item)
            
            pedidos_creados.append(pedido)
            print(f"  ✓ Creado pedido #{pedido.id} - {pedido.proveedor.nombre} - {pedido.estado.value} - ${pedido.total:.2f}")
        else:
            pedidos_creados.append(existing)
            print(f"  ↻ Ya existe pedido para {pedido_data['proveedor_id']} del {pedido_data['fecha_pedido'].date()}")
    
    db.session.commit()
    print(f"\n✓ Total pedidos creados/actualizados: {len(pedidos_creados)}")
    return pedidos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        pedidos = init_pedidos()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(pedidos)} pedidos disponibles")
        print(f"{'='*60}")
