"""
Script para inicializar costos estandarizados de prueba.
Requiere: Items activos, Facturas aprobadas (recomendado)
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
from models.factura import Factura, EstadoFactura
from models.costo_item import CostoItem

def init_costos():
    """Inicializa 10 costos estandarizados variados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE COSTOS ESTANDARIZADOS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    # Verificar facturas aprobadas (opcional pero recomendado)
    facturas_aprobadas = Factura.query.filter_by(estado=EstadoFactura.APROBADA).all()
    print(f"✓ Encontradas {len(facturas_aprobadas)} facturas aprobadas")
    
    print("\n2. INICIALIZANDO COSTOS ESTANDARIZADOS...")
    
    # Seleccionar 10 items aleatorios para crear costos
    items_seleccionados = []
    items_disponibles = items.copy()
    
    for i in range(min(10, len(items_disponibles))):
        item = choice(items_disponibles)
        items_disponibles.remove(item)
        items_seleccionados.append(item)
    
    costos_data = []
    fecha_base = datetime.now() - timedelta(days=5)
    
    for item in items_seleccionados:
        # Calcular costo promedio basado en facturas aprobadas o usar costo actual
        costo_promedio = item.costo_unitario_actual or Decimal(str(round(uniform(1, 10), 2)))
        
        # Simular variación basada en facturas
        num_facturas = randint(2, 8) if facturas_aprobadas else 0
        variacion_porcentaje = Decimal(str(round(uniform(5, 20), 2)))  # 5-20% variación
        variacion_absoluta = costo_promedio * (variacion_porcentaje / Decimal('100'))
        
        fecha_calculo = fecha_base - timedelta(days=randint(0, 4))
        
        costos_data.append({
            'item_id': item.id,
            'unidad_estandar': item.unidad,
            'costo_unitario_promedio': costo_promedio,
            'variacion_porcentaje': variacion_porcentaje,
            'variacion_absoluta': variacion_absoluta,
            'cantidad_facturas_usadas': num_facturas,
            'fecha_calculo': fecha_calculo,
            'fecha_actualizacion': fecha_calculo,
            'activo': True,
            'notas': f"Costo calculado desde {num_facturas} facturas aprobadas"
        })
    
    costos_creados = []
    for costo_data in costos_data:
        # Verificar si ya existe un costo para este item
        existing = CostoItem.query.filter_by(
            item_id=costo_data['item_id'],
            activo=True
        ).first()
        
        if not existing:
            try:
                costo = CostoItem(**costo_data)
                db.session.add(costo)
                db.session.flush()
                costos_creados.append(costo)
                
                # Obtener el item para mostrar su nombre
                item = Item.query.get(costo_data['item_id'])
                item_nombre = item.nombre if item else f"Item #{costo_data['item_id']}"
                print(f"  ✓ Creado costo #{costo.id} - {item_nombre} - ${costo.costo_unitario_promedio:.4f}/{costo.unidad_estandar}")
            except Exception as e:
                print(f"  ❌ Error al crear costo: {e}")
                db.session.rollback()
        else:
            costos_creados.append(existing)
            print(f"  ↻ Ya existe costo para item {costo_data['item_id']}")
    
    db.session.commit()
    print(f"\n✓ Total costos creados/actualizados: {len(costos_creados)}")
    return costos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        costos = init_costos()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(costos)} costos disponibles")
        print(f"{'='*60}")
