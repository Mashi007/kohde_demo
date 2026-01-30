"""
Script maestro para verificar y generar datos mock completos del módulo de Logística.
Verifica cada módulo y genera datos si no existen.
"""
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

def verificar_y_generar_datos_logistica():
    """Verifica y genera datos mock para todos los módulos de logística."""
    print("=" * 70)
    print("VERIFICACIÓN Y GENERACIÓN DE DATOS MOCK - LOGÍSTICA")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        resultados = {
            'proveedores': {'existentes': 0, 'generados': 0},
            'items': {'existentes': 0, 'generados': 0},
            'inventario': {'existentes': 0, 'generados': 0},
            'facturas': {'existentes': 0, 'generados': 0},
            'pedidos': {'existentes': 0, 'generados': 0},
            'requerimientos': {'existentes': 0, 'generados': 0},
            'pedidos_internos': {'existentes': 0, 'generados': 0},
            'labels': {'existentes': 0, 'generados': 0},
        }
        
        # 1. Verificar y generar PROVEEDORES
        print("\n" + "=" * 70)
        print("1️⃣ PROVEEDORES")
        print("=" * 70)
        try:
            from models.proveedor import Proveedor
            proveedores_existentes = db.session.query(Proveedor).count()
            resultados['proveedores']['existentes'] = proveedores_existentes
            
            if proveedores_existentes == 0:
                print("⚠️  No hay proveedores. Generando...")
                from scripts.init_mock_data import init_proveedores
                proveedores = init_proveedores()
                resultados['proveedores']['generados'] = len(proveedores)
                print(f"✅ {len(proveedores)} proveedores generados")
            else:
                print(f"✅ {proveedores_existentes} proveedores existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 2. Verificar y generar LABELS
        print("\n" + "=" * 70)
        print("2️⃣ LABELS DE ALIMENTOS")
        print("=" * 70)
        try:
            from models.item import ItemLabel
            labels_existentes = db.session.query(ItemLabel).count()
            resultados['labels']['existentes'] = labels_existentes
            
            if labels_existentes == 0:
                print("⚠️  No hay labels. Generando...")
                from scripts.init_food_labels import init_food_labels
                init_food_labels()
                labels_existentes = db.session.query(ItemLabel).count()
                resultados['labels']['generados'] = labels_existentes
                print(f"✅ {labels_existentes} labels generados")
            else:
                print(f"✅ {labels_existentes} labels existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 3. Verificar y generar ITEMS
        print("\n" + "=" * 70)
        print("3️⃣ ITEMS")
        print("=" * 70)
        try:
            from models.item import Item
            items_existentes = db.session.query(Item).count()
            resultados['items']['existentes'] = items_existentes
            
            if items_existentes == 0:
                print("⚠️  No hay items. Generando...")
                # Necesitamos proveedores y labels primero
                proveedores = db.session.query(Proveedor).all()
                labels = db.session.query(ItemLabel).all()
                
                if proveedores and labels:
                    from scripts.init_mock_data import init_items
                    items = init_items(proveedores, labels)
                    resultados['items']['generados'] = len(items) if isinstance(items, list) else 0
                    print(f"✅ Items generados")
                else:
                    print("⚠️  Se requieren proveedores y labels primero")
            else:
                print(f"✅ {items_existentes} items existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 4. Verificar y generar INVENTARIO
        print("\n" + "=" * 70)
        print("4️⃣ INVENTARIO")
        print("=" * 70)
        try:
            from models.inventario import Inventario
            inventario_existente = db.session.query(Inventario).count()
            resultados['inventario']['existentes'] = inventario_existente
            
            if inventario_existente == 0:
                print("⚠️  No hay inventario. Generando...")
                from scripts.init_inventario import init_inventario
                init_inventario()
                inventario_existente = db.session.query(Inventario).count()
                resultados['inventario']['generados'] = inventario_existente
                print(f"✅ {inventario_existente} registros de inventario generados")
            else:
                print(f"✅ {inventario_existente} registros de inventario existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 5. Verificar y generar FACTURAS
        print("\n" + "=" * 70)
        print("5️⃣ FACTURAS")
        print("=" * 70)
        try:
            from models.factura import Factura
            facturas_existentes = db.session.query(Factura).count()
            resultados['facturas']['existentes'] = facturas_existentes
            
            if facturas_existentes == 0:
                print("⚠️  No hay facturas. Generando...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    facturas = init_facturas(proveedores, items)
                    resultados['facturas']['generados'] = len(facturas) if isinstance(facturas, list) else 0
                    print(f"✅ Facturas generadas")
                else:
                    print("⚠️  Se requieren proveedores e items primero")
            else:
                print(f"✅ {facturas_existentes} facturas existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 6. Verificar y generar PEDIDOS
        print("\n" + "=" * 70)
        print("6️⃣ PEDIDOS")
        print("=" * 70)
        try:
            from models.pedido import PedidoCompra
            pedidos_existentes = db.session.query(PedidoCompra).count()
            resultados['pedidos']['existentes'] = pedidos_existentes
            
            if pedidos_existentes == 0:
                print("⚠️  No hay pedidos. Generando...")
                from scripts.init_pedidos import init_pedidos
                pedidos = init_pedidos()
                resultados['pedidos']['generados'] = len(pedidos) if isinstance(pedidos, list) else 0
                print(f"✅ Pedidos generados")
            else:
                print(f"✅ {pedidos_existentes} pedidos existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 7. Verificar y generar REQUERIMIENTOS
        print("\n" + "=" * 70)
        print("7️⃣ REQUERIMIENTOS")
        print("=" * 70)
        try:
            from models.requerimiento import Requerimiento
            requerimientos_existentes = db.session.query(Requerimiento).count()
            resultados['requerimientos']['existentes'] = requerimientos_existentes
            
            if requerimientos_existentes == 0:
                print("⚠️  No hay requerimientos. Generando...")
                from scripts.init_requerimientos import init_requerimientos
                requerimientos = init_requerimientos()
                resultados['requerimientos']['generados'] = len(requerimientos) if isinstance(requerimientos, list) else 0
                print(f"✅ Requerimientos generados")
            else:
                print(f"✅ {requerimientos_existentes} requerimientos existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # 8. Verificar y generar PEDIDOS INTERNOS
        print("\n" + "=" * 70)
        print("8️⃣ PEDIDOS INTERNOS")
        print("=" * 70)
        try:
            from models.pedido_interno import PedidoInterno
            pedidos_internos_existentes = db.session.query(PedidoInterno).count()
            resultados['pedidos_internos']['existentes'] = pedidos_internos_existentes
            
            if pedidos_internos_existentes == 0:
                print("⚠️  No hay pedidos internos. Generando...")
                from scripts.init_pedidos_internos import init_pedidos_internos
                pedidos_internos = init_pedidos_internos()
                resultados['pedidos_internos']['generados'] = len(pedidos_internos) if isinstance(pedidos_internos, list) else 0
                print(f"✅ Pedidos internos generados")
            else:
                print(f"✅ {pedidos_internos_existentes} pedidos internos existentes")
        except Exception as e:
            print(f"⚠️  Error: {str(e)}")
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN FINAL")
        print("=" * 70)
        print(f"{'Módulo':<25} {'Existentes':<15} {'Generados':<15}")
        print("-" * 70)
        for modulo, datos in resultados.items():
            print(f"{modulo.capitalize():<25} {datos['existentes']:<15} {datos['generados']:<15}")
        
        total_existentes = sum(d['existentes'] for d in resultados.values())
        total_generados = sum(d['generados'] for d in resultados.values())
        
        print("-" * 70)
        print(f"{'TOTAL':<25} {total_existentes:<15} {total_generados:<15}")
        
        print("\n✅ Verificación completada!")
        print("💡 Los datos están disponibles en los endpoints de logística")

if __name__ == '__main__':
    try:
        verificar_y_generar_datos_logistica()
    except Exception as e:
        import traceback
        print(f"\n❌ Error crítico: {str(e)}")
        print(traceback.format_exc())
