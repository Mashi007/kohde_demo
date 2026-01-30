"""
Script para verificar la integridad de los datos relacionados con Items.
Útil para identificar problemas cuando faltan datos en otros módulos.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.item import Item
from models.proveedor import Proveedor
from models.item_label import ItemLabel
from sqlalchemy import inspect

def verificar_datos_items():
    """Verifica la integridad de los datos relacionados con Items."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("VERIFICACIÓN DE DATOS DE ITEMS")
        print("=" * 60)
        
        # Verificar existencia de tablas
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        print("\n1. VERIFICACIÓN DE TABLAS:")
        tablas_requeridas = [
            'items',
            'proveedores',
            'item_label',
            'item_labels',
            'facturas',
            'factura_items',
            'inventario',
        ]
        
        for tabla in tablas_requeridas:
            existe = tabla in tables
            status = "✓" if existe else "✗"
            print(f"  {status} {tabla}: {'Existe' if existe else 'NO EXISTE'}")
        
        # Verificar items
        print("\n2. VERIFICACIÓN DE ITEMS:")
        try:
            total_items = db.session.query(Item).count()
            items_activos = db.session.query(Item).filter(Item.activo == True).count()
            print(f"  Total de items: {total_items}")
            print(f"  Items activos: {items_activos}")
            
            # Verificar items con proveedor_autorizado_id
            items_con_proveedor = db.session.query(Item).filter(
                Item.proveedor_autorizado_id.isnot(None)
            ).count()
            print(f"  Items con proveedor autorizado: {items_con_proveedor}")
            
            # Verificar items con proveedores inexistentes
            if 'proveedores' in tables:
                items_con_proveedor_invalido = db.session.query(Item).filter(
                    Item.proveedor_autorizado_id.isnot(None)
                ).all()
                
                proveedores_invalidos = []
                for item in items_con_proveedor_invalido:
                    proveedor = db.session.query(Proveedor).filter(
                        Proveedor.id == item.proveedor_autorizado_id
                    ).first()
                    if not proveedor:
                        proveedores_invalidos.append({
                            'item_id': item.id,
                            'item_codigo': item.codigo,
                            'proveedor_id': item.proveedor_autorizado_id
                        })
                
                if proveedores_invalidos:
                    print(f"  ⚠ Items con proveedor inexistente: {len(proveedores_invalidos)}")
                    for invalido in proveedores_invalidos[:5]:  # Mostrar solo los primeros 5
                        print(f"    - Item {invalido['item_codigo']} (ID: {invalido['item_id']}) -> Proveedor ID: {invalido['proveedor_id']}")
                else:
                    print(f"  ✓ Todos los proveedores son válidos")
        except Exception as e:
            print(f"  ✗ Error verificando items: {str(e)}")
        
        # Verificar labels
        print("\n3. VERIFICACIÓN DE LABELS:")
        try:
            if 'item_label' in tables:
                total_labels = db.session.query(ItemLabel).count()
                labels_activos = db.session.query(ItemLabel).filter(ItemLabel.activo == True).count()
                print(f"  Total de labels: {total_labels}")
                print(f"  Labels activos: {labels_activos}")
                
                # Verificar items con labels
                if 'item_labels' in tables:
                    from sqlalchemy import text
                    items_con_labels = db.session.execute(
                        text("SELECT COUNT(DISTINCT item_id) FROM item_labels")
                    ).scalar()
                    print(f"  Items con labels asignados: {items_con_labels}")
            else:
                print("  ⚠ Tabla item_label no existe")
        except Exception as e:
            print(f"  ✗ Error verificando labels: {str(e)}")
        
        # Verificar facturas
        print("\n4. VERIFICACIÓN DE FACTURAS:")
        try:
            if 'facturas' in tables and 'factura_items' in tables:
                from models.factura import Factura, FacturaItem
                from models.factura import EstadoFactura
                
                total_facturas = db.session.query(Factura).count()
                facturas_aprobadas = db.session.query(Factura).filter(
                    Factura.estado == EstadoFactura.APROBADA
                ).count()
                total_factura_items = db.session.query(FacturaItem).count()
                
                print(f"  Total de facturas: {total_facturas}")
                print(f"  Facturas aprobadas: {facturas_aprobadas}")
                print(f"  Total de items en facturas: {total_factura_items}")
                
                # Verificar factura_items con items inexistentes
                factura_items_sin_item = db.session.query(FacturaItem).filter(
                    FacturaItem.item_id.isnot(None)
                ).all()
                
                items_invalidos = []
                for fi in factura_items_sin_item:
                    item = db.session.query(Item).filter(Item.id == fi.item_id).first()
                    if not item:
                        items_invalidos.append({
                            'factura_item_id': fi.id,
                            'factura_id': fi.factura_id,
                            'item_id': fi.item_id
                        })
                
                if items_invalidos:
                    print(f"  ⚠ FacturaItems con items inexistentes: {len(items_invalidos)}")
                else:
                    print(f"  ✓ Todos los items en facturas son válidos")
            else:
                print("  ⚠ Tablas de facturas no existen")
        except Exception as e:
            print(f"  ✗ Error verificando facturas: {str(e)}")
        
        # Verificar inventario
        print("\n5. VERIFICACIÓN DE INVENTARIO:")
        try:
            if 'inventario' in tables:
                from models.inventario import Inventario
                total_inventario = db.session.query(Inventario).count()
                print(f"  Total de registros de inventario: {total_inventario}")
                
                # Verificar inventario con items inexistentes
                inventario_items = db.session.query(Inventario).all()
                items_invalidos = []
                for inv in inventario_items:
                    item = db.session.query(Item).filter(Item.id == inv.item_id).first()
                    if not item:
                        items_invalidos.append({
                            'inventario_id': inv.id,
                            'item_id': inv.item_id
                        })
                
                if items_invalidos:
                    print(f"  ⚠ Registros de inventario con items inexistentes: {len(items_invalidos)}")
                else:
                    print(f"  ✓ Todos los items en inventario son válidos")
            else:
                print("  ⚠ Tabla inventario no existe")
        except Exception as e:
            print(f"  ✗ Error verificando inventario: {str(e)}")
        
        print("\n" + "=" * 60)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 60)

if __name__ == '__main__':
    verificar_datos_items()
