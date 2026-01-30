"""
Script para inicializar mermas de prueba.
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
from models.merma import Merma, TipoMerma

def init_mermas():
    """Inicializa 10 mermas variadas."""
    print("=" * 60)
    print("INICIALIZACIÓN DE MERMAS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    print("\n2. INICIALIZANDO MERMAS...")
    
    tipos_merma = [
        TipoMerma.VENCIMIENTO,
        TipoMerma.DETERIORO,
        TipoMerma.PREPARACION,
        TipoMerma.SERVICIO,
        TipoMerma.OTRO
    ]
    
    ubicaciones = ['restaurante_A', 'restaurante_B', 'cocina_central', 'bodega_principal']
    motivos = [
        "Producto vencido",
        "Deterioro por mal almacenamiento",
        "Pérdida durante preparación",
        "Desperdicio en servicio",
        "Rotura de envase",
        "Contaminación",
        "Error en manipulación",
        "Condiciones de temperatura inadecuadas"
    ]
    
    mermas_data = []
    fecha_base = datetime.now() - timedelta(days=20)
    
    for i in range(10):
        item = choice(items)
        tipo = choice(tipos_merma)
        fecha_merma = fecha_base + timedelta(days=randint(0, 18))
        
        # Cantidad de merma: 1-20% del inventario típico
        cantidad = Decimal(str(round(uniform(1, 50), 2)))
        costo_unitario = item.costo_unitario_actual or Decimal(str(round(uniform(1, 10), 2)))
        costo_total = cantidad * costo_unitario
        
        mermas_data.append({
            'item_id': item.id,
            'fecha_merma': fecha_merma,
            'tipo': tipo,
            'cantidad': cantidad,
            'unidad': item.unidad,
            'costo_unitario': costo_unitario,
            'costo_total': costo_total,
            'motivo': choice(motivos),
            'ubicacion': choice(ubicaciones),
            'registrado_por': randint(1, 5),
            'fecha_registro': fecha_merma + timedelta(hours=randint(1, 6))
        })
    
    mermas_creadas = []
    for merma_data in mermas_data:
        # Verificar si ya existe
        existing = Merma.query.filter_by(
            item_id=merma_data['item_id'],
            fecha_merma=merma_data['fecha_merma']
        ).first()
        
        if not existing:
            merma = Merma(**merma_data)
            db.session.add(merma)
            db.session.flush()
            mermas_creadas.append(merma)
            
            # Obtener el item para mostrar su nombre
            item = Item.query.get(merma_data['item_id'])
            item_nombre = item.nombre if item else f"Item #{merma_data['item_id']}"
            print(f"  ✓ Creada merma #{merma.id} - {item_nombre} - {merma.tipo.value} - ${merma.costo_total:.2f}")
        else:
            mermas_creadas.append(existing)
            print(f"  ↻ Ya existe merma para item {merma_data['item_id']} del {merma_data['fecha_merma'].date()}")
    
    db.session.commit()
    print(f"\n✓ Total mermas creadas/actualizadas: {len(mermas_creadas)}")
    return mermas_creadas

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        mermas = init_mermas()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(mermas)} mermas disponibles")
        print(f"{'='*60}")
