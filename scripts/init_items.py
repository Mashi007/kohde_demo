"""
Script para inicializar items de prueba.
Requiere: Proveedores y Labels (opcional)
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.proveedor import Proveedor
from models.item import Item
from models.item_label import ItemLabel

def init_items():
    """Inicializa 50 items variados de prueba."""
    print("=" * 60)
    print("INICIALIZACIÓN DE ITEMS")
    print("=" * 60)
    
    # Verificar proveedores
    proveedores = Proveedor.query.filter_by(activo=True).all()
    if not proveedores:
        print("\n⚠ No hay proveedores activos.")
        print("  Ejecuta primero: python scripts/init_mock_data.py (para crear proveedores)")
        print("  O crea proveedores manualmente.")
        return []
    
    print(f"\n✓ Encontrados {len(proveedores)} proveedores activos")
    
    # Verificar labels (opcional)
    labels = ItemLabel.query.all()
    if not labels:
        print("⚠ No hay labels. Los items se crearán sin labels.")
        print("  Para agregar labels ejecuta: python scripts/init_food_labels.py")
    else:
        print(f"✓ Encontradas {len(labels)} labels")
    
    # Mapear labels por categoría para facilitar la asignación
    labels_map = {}
    for label in labels:
        cat = label.categoria_principal
        if cat not in labels_map:
            labels_map[cat] = []
        labels_map[cat].append(label)
    
    print("\n2. INICIALIZANDO ITEMS...")
    
    items_data = [
        # VERDURAS Y HORTALIZAS (7 items)
        {
            'codigo': 'MP-20240130-0001', 'nombre': 'Cebolla Blanca', 'descripcion': 'Cebolla blanca fresca',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 40.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.50, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0002', 'nombre': 'Tomate Fresco', 'descripcion': 'Tomate rojo fresco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 18.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 2.00, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0003', 'nombre': 'Papa', 'descripcion': 'Papa amarilla',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 77.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 0.80, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0010', 'nombre': 'Zanahoria', 'descripcion': 'Zanahoria fresca',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 41.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.20, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0011', 'nombre': 'Lechuga', 'descripcion': 'Lechuga fresca',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 15.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.80, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0012', 'nombre': 'Ajo', 'descripcion': 'Ajo fresco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 149.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 3.50, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        {
            'codigo': 'MP-20240130-0013', 'nombre': 'Pimiento Rojo', 'descripcion': 'Pimiento rojo fresco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 31.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 2.80, 'activo': True,
            'labels': labels_map.get('Verduras y hortalizas', [])[:1] if labels_map.get('Verduras y hortalizas') else []
        },
        
        # FRUTAS (5 items)
        {
            'codigo': 'MP-20240130-0017', 'nombre': 'Limón', 'descripcion': 'Limón fresco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 29.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.80, 'activo': True,
            'labels': labels_map.get('Frutas', [])[:1] if labels_map.get('Frutas') else []
        },
        {
            'codigo': 'MP-20240130-0018', 'nombre': 'Plátano', 'descripcion': 'Plátano maduro',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 89.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.50, 'activo': True,
            'labels': labels_map.get('Frutas', [])[:1] if labels_map.get('Frutas') else []
        },
        {
            'codigo': 'MP-20240130-0019', 'nombre': 'Manzana', 'descripcion': 'Manzana roja',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 52.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 2.20, 'activo': True,
            'labels': labels_map.get('Frutas', [])[:1] if labels_map.get('Frutas') else []
        },
        {
            'codigo': 'MP-20240130-0020', 'nombre': 'Fresas', 'descripcion': 'Fresas frescas',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 32.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 4.50, 'activo': True,
            'labels': labels_map.get('Frutas', [])[:1] if labels_map.get('Frutas') else []
        },
        {
            'codigo': 'MP-20240130-0021', 'nombre': 'Naranja', 'descripcion': 'Naranja dulce',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 47.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.60, 'activo': True,
            'labels': labels_map.get('Frutas', [])[:1] if labels_map.get('Frutas') else []
        },
        
        # CARNES (7 items)
        {
            'codigo': 'MP-20240130-0004', 'nombre': 'Pechuga de Pollo', 'descripcion': 'Pechuga de pollo fresca',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 165.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 5.50, 'activo': True,
            'labels': labels_map.get('Aves y pollo', [])[:1] if labels_map.get('Aves y pollo') else []
        },
        {
            'codigo': 'MP-20240130-0005', 'nombre': 'Carne de Res Molida', 'descripcion': 'Carne de res molida',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 250.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 8.00, 'activo': True,
            'labels': labels_map.get('Carnes rojas', [])[:1] if labels_map.get('Carnes rojas') else []
        },
        {
            'codigo': 'MP-20240130-0022', 'nombre': 'Muslo de Pollo', 'descripcion': 'Muslo de pollo con hueso',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 180.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 4.50, 'activo': True,
            'labels': labels_map.get('Aves y pollo', [])[:1] if labels_map.get('Aves y pollo') else []
        },
        {
            'codigo': 'MP-20240130-0023', 'nombre': 'Carne de Res en Trozos', 'descripcion': 'Carne de res en trozos para guiso',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 250.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 7.50, 'activo': True,
            'labels': labels_map.get('Carnes rojas', [])[:1] if labels_map.get('Carnes rojas') else []
        },
        {
            'codigo': 'MP-20240130-0024', 'nombre': 'Carne de Cerdo', 'descripcion': 'Carne de cerdo fresca',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 242.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 6.00, 'activo': True,
            'labels': labels_map.get('Carnes rojas', [])[:1] if labels_map.get('Carnes rojas') else []
        },
        {
            'codigo': 'MP-20240130-0025', 'nombre': 'Pollo Entero', 'descripcion': 'Pollo entero fresco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 165.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 4.80, 'activo': True,
            'labels': labels_map.get('Aves y pollo', [])[:1] if labels_map.get('Aves y pollo') else []
        },
        {
            'codigo': 'MP-20240130-0026', 'nombre': 'Ternera', 'descripcion': 'Carne de ternera',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 172.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 9.50, 'activo': True,
            'labels': labels_map.get('Carnes rojas', [])[:1] if labels_map.get('Carnes rojas') else []
        },
        {
            'codigo': 'MP-20240130-0027', 'nombre': 'Pescado Fresco', 'descripcion': 'Pescado fresco del día',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 206.0,
            'proveedor_autorizado_id': proveedores[1].id if len(proveedores) > 1 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 6.50, 'activo': True,
            'labels': labels_map.get('Pescados y mariscos', [])[:1] if labels_map.get('Pescados y mariscos') else []
        },
        
        # LÁCTEOS Y HUEVOS (6 items)
        {
            'codigo': 'MP-20240130-0006', 'nombre': 'Leche Entera', 'descripcion': 'Leche entera pasteurizada',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'litro', 'calorias_por_unidad': 61.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.20, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        {
            'codigo': 'MP-20240130-0007', 'nombre': 'Queso Mozzarella', 'descripcion': 'Queso mozzarella rallado',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 300.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 6.50, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        {
            'codigo': 'MP-20240130-0029', 'nombre': 'Huevos', 'descripcion': 'Huevos de gallina AA',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'docena', 'calorias_por_unidad': 155.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 2.50, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        {
            'codigo': 'MP-20240130-0030', 'nombre': 'Queso Cheddar', 'descripcion': 'Queso cheddar',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 402.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 7.00, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        {
            'codigo': 'MP-20240130-0031', 'nombre': 'Mantequilla', 'descripcion': 'Mantequilla sin sal',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 717.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 5.50, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        {
            'codigo': 'MP-20240130-0033', 'nombre': 'Yogurt Natural', 'descripcion': 'Yogurt natural',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'litro', 'calorias_por_unidad': 59.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 2.20, 'activo': True,
            'labels': labels_map.get('Lácteos y huevos', [])[:1] if labels_map.get('Lácteos y huevos') else []
        },
        
        # PRODUCTOS SECOS Y GRANOS (7 items)
        {
            'codigo': 'MP-20240130-0008', 'nombre': 'Arroz Blanco', 'descripcion': 'Arroz blanco de primera',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 365.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.80, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0009', 'nombre': 'Pasta Espagueti', 'descripcion': 'Pasta espagueti',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 371.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 2.50, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0035', 'nombre': 'Harina de Trigo', 'descripcion': 'Harina de trigo todo uso',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 364.0,
            'proveedor_autorizado_id': proveedores[4].id if len(proveedores) > 4 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.50, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0036', 'nombre': 'Azúcar Blanca', 'descripcion': 'Azúcar blanca refinada',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 387.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.20, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0037', 'nombre': 'Frijoles Negros', 'descripcion': 'Frijoles negros secos',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 341.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 2.20, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0039', 'nombre': 'Pasta Penne', 'descripcion': 'Pasta penne',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 371.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 2.50, 'activo': True,
            'labels': labels_map.get('Productos secos y granos', [])[:1] if labels_map.get('Productos secos y granos') else []
        },
        {
            'codigo': 'MP-20240130-0042', 'nombre': 'Sal', 'descripcion': 'Sal de mesa',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 0.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 0.50, 'activo': True,
            'labels': labels_map.get('Condimentos y especias', [])[:1] if labels_map.get('Condimentos y especias') else []
        },
        
        # CONDIMENTOS Y ESPECIAS (5 items)
        {
            'codigo': 'MP-20240130-0043', 'nombre': 'Pimienta Negra', 'descripcion': 'Pimienta negra molida',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 251.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 8.00, 'activo': True,
            'labels': labels_map.get('Condimentos y especias', [])[:1] if labels_map.get('Condimentos y especias') else []
        },
        {
            'codigo': 'MP-20240130-0044', 'nombre': 'Comino', 'descripcion': 'Comino molido',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 375.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 6.50, 'activo': True,
            'labels': labels_map.get('Condimentos y especias', [])[:1] if labels_map.get('Condimentos y especias') else []
        },
        {
            'codigo': 'MP-20240130-0045', 'nombre': 'Orégano', 'descripcion': 'Orégano seco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'kg', 'calorias_por_unidad': 265.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 12.00, 'activo': True,
            'labels': labels_map.get('Condimentos y especias', [])[:1] if labels_map.get('Condimentos y especias') else []
        },
        {
            'codigo': 'MP-20240130-0046', 'nombre': 'Aceite de Oliva', 'descripcion': 'Aceite de oliva extra virgen',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'litro', 'calorias_por_unidad': 884.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 8.50, 'activo': True,
            'labels': labels_map.get('Salsas y envasados', [])[:1] if labels_map.get('Salsas y envasados') else []
        },
        {
            'codigo': 'MP-20240130-0047', 'nombre': 'Vinagre', 'descripcion': 'Vinagre blanco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'litro', 'calorias_por_unidad': 18.0,
            'proveedor_autorizado_id': proveedores[0].id if proveedores else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.50, 'activo': True,
            'labels': labels_map.get('Salsas y envasados', [])[:1] if labels_map.get('Salsas y envasados') else []
        },
        
        # BEBIDAS (6 items)
        {
            'codigo': 'BE-20240130-0001', 'nombre': 'Coca Cola 500ml', 'descripcion': 'Coca Cola en botella de 500ml',
            'categoria': 'bebida', 'unidad': 'unidad', 'calorias_por_unidad': 210.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 0.75, 'activo': True,
            'labels': labels_map.get('Bebidas gaseosas', [])[:1] if labels_map.get('Bebidas gaseosas') else []
        },
        {
            'codigo': 'BE-20240130-0002', 'nombre': 'Agua Mineral 500ml', 'descripcion': 'Agua mineral sin gas',
            'categoria': 'bebida', 'unidad': 'unidad', 'calorias_por_unidad': 0.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 0.50, 'activo': True,
            'labels': labels_map.get('Bebidas no alcohólicas', [])[:1] if labels_map.get('Bebidas no alcohólicas') else []
        },
        {
            'codigo': 'BE-20240130-0048', 'nombre': 'Sprite 500ml', 'descripcion': 'Sprite en botella de 500ml',
            'categoria': 'bebida', 'unidad': 'unidad', 'calorias_por_unidad': 192.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 0.75, 'activo': True,
            'labels': labels_map.get('Bebidas gaseosas', [])[:1] if labels_map.get('Bebidas gaseosas') else []
        },
        {
            'codigo': 'BE-20240130-0049', 'nombre': 'Jugo de Naranja 1L', 'descripcion': 'Jugo de naranja natural',
            'categoria': 'bebida', 'unidad': 'unidad', 'calorias_por_unidad': 45.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 2.50, 'activo': True,
            'labels': labels_map.get('Bebidas no alcohólicas', [])[:1] if labels_map.get('Bebidas no alcohólicas') else []
        },
        {
            'codigo': 'BE-20240130-0050', 'nombre': 'Café Molido', 'descripcion': 'Café molido tostado',
            'categoria': 'bebida', 'unidad': 'kg', 'calorias_por_unidad': 0.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 6.00, 'activo': True,
            'labels': labels_map.get('Bebidas no alcohólicas', [])[:1] if labels_map.get('Bebidas no alcohólicas') else []
        },
        {
            'codigo': 'BE-20240130-0051', 'nombre': 'Té Negro', 'descripcion': 'Té negro en bolsitas',
            'categoria': 'bebida', 'unidad': 'caja', 'calorias_por_unidad': 2.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 3.50, 'activo': True,
            'labels': labels_map.get('Bebidas no alcohólicas', [])[:1] if labels_map.get('Bebidas no alcohólicas') else []
        },
        {
            'codigo': 'BE-20240130-0052', 'nombre': 'Cerveza Nacional', 'descripcion': 'Cerveza nacional 330ml',
            'categoria': 'bebida', 'unidad': 'unidad', 'calorias_por_unidad': 43.0,
            'proveedor_autorizado_id': proveedores[2].id if len(proveedores) > 2 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.20, 'activo': True,
            'labels': labels_map.get('Bebidas alcohólicas', [])[:1] if labels_map.get('Bebidas alcohólicas') else []
        },
        
        # LIMPIEZA Y DESECHABLES (5 items)
        {
            'codigo': 'LI-20240130-0001', 'nombre': 'Detergente Líquido', 'descripcion': 'Detergente líquido para platos',
            'categoria': 'limpieza', 'unidad': 'litro', 'calorias_por_unidad': None,
            'proveedor_autorizado_id': proveedores[3].id if len(proveedores) > 3 else None, 'tiempo_entrega_dias': 3,
            'costo_unitario_actual': 3.50, 'activo': True,
            'labels': labels_map.get('Artículos de limpieza y desechables', [])[:1] if labels_map.get('Artículos de limpieza y desechables') else []
        },
        {
            'codigo': 'LI-20240130-0002', 'nombre': 'Servilletas', 'descripcion': 'Servilletas desechables',
            'categoria': 'limpieza', 'unidad': 'paquete', 'calorias_por_unidad': None,
            'proveedor_autorizado_id': proveedores[3].id if len(proveedores) > 3 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 2.00, 'activo': True,
            'labels': labels_map.get('Artículos de limpieza y desechables', [])[:1] if labels_map.get('Artículos de limpieza y desechables') else []
        },
        {
            'codigo': 'LI-20240130-0054', 'nombre': 'Guantes Desechables', 'descripcion': 'Guantes de nitrilo desechables',
            'categoria': 'limpieza', 'unidad': 'caja', 'calorias_por_unidad': None,
            'proveedor_autorizado_id': proveedores[3].id if len(proveedores) > 3 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 5.00, 'activo': True,
            'labels': labels_map.get('Artículos de limpieza y desechables', [])[:1] if labels_map.get('Artículos de limpieza y desechables') else []
        },
        {
            'codigo': 'LI-20240130-0055', 'nombre': 'Bolsas de Basura', 'descripcion': 'Bolsas de basura grandes',
            'categoria': 'limpieza', 'unidad': 'rollo', 'calorias_por_unidad': None,
            'proveedor_autorizado_id': proveedores[3].id if len(proveedores) > 3 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 4.50, 'activo': True,
            'labels': labels_map.get('Artículos de limpieza y desechables', [])[:1] if labels_map.get('Artículos de limpieza y desechables') else []
        },
        {
            'codigo': 'LI-20240130-0056', 'nombre': 'Vasos Desechables', 'descripcion': 'Vasos desechables 250ml',
            'categoria': 'limpieza', 'unidad': 'paquete', 'calorias_por_unidad': None,
            'proveedor_autorizado_id': proveedores[3].id if len(proveedores) > 3 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 3.00, 'activo': True,
            'labels': labels_map.get('Otros / suministros menores', [])[:1] if labels_map.get('Otros / suministros menores') else []
        },
        
        # PANADERÍA (3 items)
        {
            'codigo': 'MP-20240130-0058', 'nombre': 'Pan de Molde', 'descripcion': 'Pan de molde blanco',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'unidad', 'calorias_por_unidad': 265.0,
            'proveedor_autorizado_id': proveedores[4].id if len(proveedores) > 4 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 1.80, 'activo': True,
            'labels': labels_map.get('Panadería y repostería', [])[:1] if labels_map.get('Panadería y repostería') else []
        },
        {
            'codigo': 'MP-20240130-0059', 'nombre': 'Tortillas', 'descripcion': 'Tortillas de harina',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'paquete', 'calorias_por_unidad': 218.0,
            'proveedor_autorizado_id': proveedores[4].id if len(proveedores) > 4 else None, 'tiempo_entrega_dias': 1,
            'costo_unitario_actual': 2.50, 'activo': True,
            'labels': labels_map.get('Panadería y repostería', [])[:1] if labels_map.get('Panadería y repostería') else []
        },
        {
            'codigo': 'MP-20240130-0060', 'nombre': 'Levadura', 'descripcion': 'Levadura seca instantánea',
            'categoria': 'MATERIA_PRIMA', 'unidad': 'paquete', 'calorias_por_unidad': 105.0,
            'proveedor_autorizado_id': proveedores[4].id if len(proveedores) > 4 else None, 'tiempo_entrega_dias': 2,
            'costo_unitario_actual': 1.20, 'activo': True,
            'labels': labels_map.get('Panadería y repostería', [])[:1] if labels_map.get('Panadería y repostería') else []
        }
    ]
    
    items_creados = []
    for item_data in items_data:
        # Separar labels del resto de datos
        labels = item_data.pop('labels', [])
        
        existing = Item.query.filter_by(codigo=item_data['codigo']).first()
        if not existing:
            item = Item(**item_data)
            db.session.add(item)
            db.session.flush()  # Para obtener el ID
            
            # Asignar labels si existen
            if labels:
                item.labels = labels
            
            items_creados.append(item)
            print(f"  ✓ Creado: {item_data['nombre']} ({item_data['codigo']})")
        else:
            items_creados.append(existing)
            print(f"  ↻ Ya existe: {item_data['nombre']} ({item_data['codigo']})")
    
    db.session.commit()
    print(f"\n✓ Total items creados/actualizados: {len(items_creados)}")
    return items_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        items = init_items()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(items)} items disponibles")
        print(f"{'='*60}")
