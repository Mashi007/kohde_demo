"""
Script para inicializar facturas de prueba.
Requiere: Proveedores e Items activos
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.proveedor import Proveedor
from models.item import Item
from models.factura import Factura, FacturaItem, EstadoFactura, TipoFactura

def init_facturas():
    """Inicializa 20 facturas de prueba con items relacionados."""
    print("=" * 60)
    print("INICIALIZACIÓN DE FACTURAS")
    print("=" * 60)
    
    # Verificar proveedores
    proveedores = Proveedor.query.filter_by(activo=True).all()
    if not proveedores:
        print("\n⚠ No hay proveedores activos.")
        print("  Ejecuta primero: python scripts/init_mock_data.py (para crear proveedores)")
        return []
    
    print(f"\n✓ Encontrados {len(proveedores)} proveedores activos")
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items:
        print("\n⚠ No hay items activos.")
        print("  Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"✓ Encontrados {len(items)} items activos")
    print("\n4. INICIALIZANDO FACTURAS (20 FACTURAS)...")
    
    # Crear mapa de items por categoría para facilitar selección
    items_por_proveedor = {}
    for item in items:
        prov_id = item.proveedor_autorizado_id
        if prov_id:
            if prov_id not in items_por_proveedor:
                items_por_proveedor[prov_id] = []
            items_por_proveedor[prov_id].append(item)
    
    # Si un proveedor no tiene items, usar items generales
    items_generales = [item for item in items if item.categoria == 'MATERIA_PRIMA'][:20]
    
    # Generar 20 facturas variadas
    facturas_data = []
    base_date = datetime.now()
    
    # Facturas aprobadas (8 facturas) - para calcular costos promedio
    for i in range(1, 9):
        prov = proveedores[i % len(proveedores)]
        prov_items = items_por_proveedor.get(prov.id, items_generales[:5])
        if not prov_items:
            prov_items = items_generales[:5]
        
        num_items = min(3, len(prov_items))
        factura_items = []
        subtotal = Decimal('0')
        
        for j in range(num_items):
            item = prov_items[j % len(prov_items)]
            cantidad = Decimal(str(10 + (i * 2) + j))
            precio = item.costo_unitario_actual or Decimal('1.00')
            if precio is None:
                precio = Decimal('1.00')
            item_subtotal = cantidad * precio
            subtotal += item_subtotal
            
            factura_items.append({
                'item': item,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'cantidad_aprobada': cantidad,  # Aprobada completamente
                'unidad': item.unidad,
                'descripcion': item.nombre
            })
        
        iva = subtotal * Decimal('0.12')  # IVA 12%
        total = subtotal + iva
        
        facturas_data.append({
            'numero_factura': f'FAC-2024-{i:03d}',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': prov.id,
            'fecha_emision': base_date - timedelta(days=60-i*5),
            'fecha_recepcion': base_date - timedelta(days=59-i*5),
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'estado': EstadoFactura.APROBADA,
            'aprobado_por': 1,
            'fecha_aprobacion': base_date - timedelta(days=58-i*5),
            'items': factura_items
        })
    
    # Facturas pendientes (5 facturas)
    for i in range(9, 14):
        prov = proveedores[i % len(proveedores)]
        prov_items = items_por_proveedor.get(prov.id, items_generales[:5])
        if not prov_items:
            prov_items = items_generales[:5]
        
        num_items = min(4, len(prov_items))
        factura_items = []
        subtotal = Decimal('0')
        
        for j in range(num_items):
            item = prov_items[j % len(prov_items)]
            cantidad = Decimal(str(15 + (i * 2) + j))
            precio = item.costo_unitario_actual or Decimal('1.00')
            if precio is None:
                precio = Decimal('1.00')
            item_subtotal = cantidad * precio
            subtotal += item_subtotal
            
            factura_items.append({
                'item': item,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'cantidad_aprobada': None,  # Pendiente de aprobación
                'unidad': item.unidad,
                'descripcion': item.nombre
            })
        
        iva = subtotal * Decimal('0.12')
        total = subtotal + iva
        
        facturas_data.append({
            'numero_factura': f'FAC-2024-{i:03d}',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': prov.id,
            'fecha_emision': base_date - timedelta(days=20-i+9),
            'fecha_recepcion': base_date - timedelta(days=19-i+9),
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'estado': EstadoFactura.PENDIENTE,
            'items': factura_items
        })
    
    # Facturas parciales (4 facturas)
    for i in range(14, 18):
        prov = proveedores[i % len(proveedores)]
        prov_items = items_por_proveedor.get(prov.id, items_generales[:5])
        if not prov_items:
            prov_items = items_generales[:5]
        
        num_items = min(3, len(prov_items))
        factura_items = []
        subtotal = Decimal('0')
        
        for j in range(num_items):
            item = prov_items[j % len(prov_items)]
            cantidad = Decimal(str(20 + (i * 2) + j))
            precio = item.costo_unitario_actual or Decimal('1.00')
            if precio is None:
                precio = Decimal('1.00')
            item_subtotal = cantidad * precio
            subtotal += item_subtotal
            
            # Aprobar parcialmente (80% de la cantidad)
            cantidad_aprobada = cantidad * Decimal('0.8')
            
            factura_items.append({
                'item': item,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'cantidad_aprobada': cantidad_aprobada,
                'unidad': item.unidad,
                'descripcion': item.nombre
            })
        
        iva = subtotal * Decimal('0.12')
        total = subtotal + iva
        
        facturas_data.append({
            'numero_factura': f'FAC-2024-{i:03d}',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': prov.id,
            'fecha_emision': base_date - timedelta(days=10-i+14),
            'fecha_recepcion': base_date - timedelta(days=9-i+14),
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'estado': EstadoFactura.PARCIAL,
            'aprobado_por': 1,
            'fecha_aprobacion': base_date - timedelta(days=8-i+14),
            'observaciones': 'Aprobación parcial - pendiente revisión de algunos items',
            'items': factura_items
        })
    
    # Facturas rechazadas (3 facturas)
    for i in range(18, 21):
        prov = proveedores[i % len(proveedores)]
        prov_items = items_por_proveedor.get(prov.id, items_generales[:5])
        if not prov_items:
            prov_items = items_generales[:5]
        
        num_items = min(2, len(prov_items))
        factura_items = []
        subtotal = Decimal('0')
        
        for j in range(num_items):
            item = prov_items[j % len(prov_items)]
            cantidad = Decimal(str(25 + (i * 2) + j))
            precio = item.costo_unitario_actual or Decimal('1.00')
            if precio is None:
                precio = Decimal('1.00')
            item_subtotal = cantidad * precio
            subtotal += item_subtotal
            
            factura_items.append({
                'item': item,
                'cantidad': cantidad,
                'precio_unitario': precio,
                'cantidad_aprobada': Decimal('0'),  # Rechazada
                'unidad': item.unidad,
                'descripcion': item.nombre
            })
        
        iva = subtotal * Decimal('0.12')
        total = subtotal + iva
        
        facturas_data.append({
            'numero_factura': f'FAC-2024-{i:03d}',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': prov.id,
            'fecha_emision': base_date - timedelta(days=5-i+18),
            'fecha_recepcion': base_date - timedelta(days=4-i+18),
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
            'estado': EstadoFactura.RECHAZADA,
            'aprobado_por': 1,
            'fecha_aprobacion': base_date - timedelta(days=3-i+18),
            'observaciones': 'Factura rechazada - productos no cumplen especificaciones',
            'items': factura_items
        })
    
    facturas_creadas = []
    for fact_data in facturas_data:
        # Separar items de la factura
        items_factura = fact_data.pop('items', [])
        
        if not items_factura:
            print(f"  ⚠ Saltando factura {fact_data['numero_factura']}: sin items")
            continue
        
        existing = Factura.query.filter_by(numero_factura=fact_data['numero_factura']).first()
        if not existing:
            factura = Factura(**fact_data)
            db.session.add(factura)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de la factura
            for item_fact in items_factura:
                item = item_fact['item']
                cantidad = Decimal(str(item_fact['cantidad']))
                precio_unitario = Decimal(str(item_fact['precio_unitario']))
                subtotal = cantidad * precio_unitario
                
                cantidad_aprobada = None
                if item_fact.get('cantidad_aprobada') is not None:
                    cantidad_aprobada = Decimal(str(item_fact['cantidad_aprobada']))
                
                factura_item = FacturaItem(
                    factura_id=factura.id,
                    item_id=item.id,
                    cantidad_facturada=cantidad,
                    cantidad_aprobada=cantidad_aprobada,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                    unidad=item_fact.get('unidad', item.unidad),
                    descripcion=item_fact.get('descripcion', item.nombre)
                )
                db.session.add(factura_item)
            
            facturas_creadas.append(factura)
            estado_str = fact_data['estado'].value if hasattr(fact_data['estado'], 'value') else str(fact_data['estado'])
            print(f"  ✓ Creada: {fact_data['numero_factura']} - ${fact_data['total']:.2f} ({estado_str}) - {len(items_factura)} items")
        else:
            facturas_creadas.append(existing)
            print(f"  ↻ Ya existe: {fact_data['numero_factura']}")
    
    db.session.commit()
    print(f"\n✓ Total facturas creadas: {len(facturas_creadas)}")
    return facturas_creadas

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        facturas = init_facturas()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(facturas)} facturas disponibles")
        print(f"{'='*60}")
