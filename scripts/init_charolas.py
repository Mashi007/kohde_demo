"""
Script para inicializar charolas de prueba.
Requiere: Items activos, Recetas activas (opcional)
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
from models.receta import Receta
from models.charola import Charola, CharolaItem

def init_charolas():
    """Inicializa 10 charolas variadas."""
    print("=" * 60)
    print("INICIALIZACIÓN DE CHAROLAS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n❌ Error: No hay items activos.")
        print("   Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    
    # Verificar recetas (opcional)
    recetas = Receta.query.filter_by(activa=True).all()
    print(f"✓ Encontradas {len(recetas)} recetas activas")
    
    print("\n2. INICIALIZANDO CHAROLAS...")
    
    tiempos_comida = ['desayuno', 'almuerzo', 'cena']
    ubicaciones = ['restaurante_A', 'restaurante_B', 'cocina_central']
    
    charolas_data = []
    fecha_base = datetime.now() - timedelta(days=7)
    
    for i in range(10):
        tiempo_comida = choice(tiempos_comida)
        fecha_servicio = fecha_base + timedelta(days=randint(0, 6))
        personas_servidas = randint(50, 200)
        
        # Seleccionar 2-4 items/recetas para la charola
        items_charola = []
        num_items = randint(2, 4)
        
        for j in range(num_items):
            # 70% probabilidad de usar receta, 30% item directo
            usar_receta = uniform(0, 1) > 0.3 and recetas
            
            if usar_receta:
                receta = choice(recetas)
                cantidad = Decimal(str(round(uniform(10, 50), 2)))
                precio_unitario = Decimal(str(round(uniform(5, 15), 2)))
                costo_unitario = receta.costo_total / Decimal(str(receta.porciones)) if receta.porciones > 0 else Decimal('5')
                subtotal = cantidad * precio_unitario
                costo_subtotal = cantidad * costo_unitario
                
                items_charola.append({
                    'item_id': None,
                    'receta_id': receta.id,
                    'nombre_item': receta.nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'costo_unitario': costo_unitario,
                    'subtotal': subtotal,
                    'costo_subtotal': costo_subtotal
                })
            else:
                item = choice(items)
                cantidad = Decimal(str(round(uniform(5, 30), 2)))
                precio_unitario = Decimal(str(round(uniform(3, 12), 2)))
                costo_unitario = item.costo_unitario_actual or Decimal('2')
                subtotal = cantidad * precio_unitario
                costo_subtotal = cantidad * costo_unitario
                
                items_charola.append({
                    'item_id': item.id,
                    'receta_id': None,
                    'nombre_item': item.nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'costo_unitario': costo_unitario,
                    'subtotal': subtotal,
                    'costo_subtotal': costo_subtotal
                })
        
        total_ventas = sum(item['subtotal'] for item in items_charola)
        costo_total = sum(item['costo_subtotal'] for item in items_charola)
        ganancia = total_ventas - costo_total
        
        numero_charola = f"CHR-{fecha_servicio.strftime('%Y%m%d')}-{i+1:03d}"
        
        charolas_data.append({
            'numero_charola': numero_charola,
            'fecha_servicio': fecha_servicio,
            'ubicacion': choice(ubicaciones),
            'tiempo_comida': tiempo_comida,
            'personas_servidas': personas_servidas,
            'total_ventas': total_ventas,
            'costo_total': costo_total,
            'ganancia': ganancia,
            'observaciones': f"Charola {tiempo_comida} - {personas_servidas} personas",
            'fecha_registro': fecha_servicio,
            'items': items_charola
        })
    
    charolas_creadas = []
    for charola_data in charolas_data:
        items_data = charola_data.pop('items')
        
        # Verificar si ya existe
        existing = Charola.query.filter_by(
            numero_charola=charola_data['numero_charola']
        ).first()
        
        if not existing:
            charola = Charola(**charola_data)
            db.session.add(charola)
            db.session.flush()
            
            # Crear items de la charola
            for item_data in items_data:
                charola_item = CharolaItem(
                    charola_id=charola.id,
                    **item_data
                )
                db.session.add(charola_item)
            
            charolas_creadas.append(charola)
            print(f"  ✓ Creada charola #{charola.id} - {charola.numero_charola} - {charola.tiempo_comida} - ${charola.total_ventas:.2f}")
        else:
            charolas_creadas.append(existing)
            print(f"  ↻ Ya existe charola {charola_data['numero_charola']}")
    
    db.session.commit()
    print(f"\n✓ Total charolas creadas/actualizadas: {len(charolas_creadas)}")
    return charolas_creadas

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        charolas = init_charolas()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(charolas)} charolas disponibles")
        print(f"{'='*60}")
