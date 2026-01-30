"""
Script para inicializar requerimientos de prueba.
Requiere: Items activos
"""
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta, time
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.item import Item
from models.requerimiento import Requerimiento, RequerimientoItem, EstadoRequerimiento

def init_requerimientos():
    """Inicializa 10 requerimientos variados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE REQUERIMIENTOS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    print("\n2. INICIALIZANDO REQUERIMIENTOS...")
    
    estados = [EstadoRequerimiento.PENDIENTE, EstadoRequerimiento.ENTREGADO, EstadoRequerimiento.CANCELADO]
    usuarios = [
        {'solicitante': 1, 'receptor': 2},
        {'solicitante': 2, 'receptor': 3},
        {'solicitante': 3, 'receptor': 1},
        {'solicitante': 4, 'receptor': 5},
        {'solicitante': 5, 'receptor': 6},
    ]
    
    requerimientos_data = []
    fecha_base = datetime.now() - timedelta(days=10)
    
    for i in range(10):
        estado = choice(estados)
        fecha_req = fecha_base + timedelta(days=randint(0, 8))
        usuario = choice(usuarios)
        
        # Seleccionar 2-4 items aleatorios
        items_req = []
        items_seleccionados = []
        num_items = randint(2, 4)
        
        for _ in range(num_items):
            item = choice(items)
            if item.id not in items_seleccionados:
                items_seleccionados.append(item.id)
                cantidad_solicitada = Decimal(str(round(uniform(10, 100), 2)))
                cantidad_entregada = None
                hora_entrega = None
                
                if estado == EstadoRequerimiento.ENTREGADO:
                    cantidad_entregada = cantidad_solicitada * Decimal(str(round(uniform(0.95, 1.0), 2)))  # 95-100% entregado
                    hora_entrega = time(randint(8, 18), randint(0, 59))
                
                items_req.append({
                    'item_id': item.id,
                    'cantidad_solicitada': cantidad_solicitada,
                    'cantidad_entregada': cantidad_entregada,
                    'hora_entrega': hora_entrega
                })
        
        requerimientos_data.append({
            'solicitante': usuario['solicitante'],
            'receptor': usuario['receptor'],
            'fecha': fecha_req,
            'estado': estado,
            'observaciones': f"Requerimiento #{i+1} - Salida de bodega",
            'items': items_req
        })
    
    requerimientos_creados = []
    for req_data in requerimientos_data:
        items_data = req_data.pop('items')
        
        # Verificar si ya existe
        existing = Requerimiento.query.filter_by(
            fecha=req_data['fecha'],
            solicitante=req_data['solicitante']
        ).first()
        
        if not existing:
            requerimiento = Requerimiento(**req_data)
            db.session.add(requerimiento)
            db.session.flush()
            
            # Crear items del requerimiento
            for item_data in items_data:
                req_item = RequerimientoItem(
                    requerimiento_id=requerimiento.id,
                    **item_data
                )
                db.session.add(req_item)
            
            requerimientos_creados.append(requerimiento)
            print(f"  ✓ Creado requerimiento #{requerimiento.id} - {req_data['estado'].value} - {len(items_data)} items")
        else:
            requerimientos_creados.append(existing)
            print(f"  ↻ Ya existe requerimiento del {req_data['fecha'].date()}")
    
    db.session.commit()
    print(f"\n✓ Total requerimientos creados/actualizados: {len(requerimientos_creados)}")
    return requerimientos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        requerimientos = init_requerimientos()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(requerimientos)} requerimientos disponibles")
        print(f"{'='*60}")
