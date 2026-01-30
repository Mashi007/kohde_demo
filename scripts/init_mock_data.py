"""
Script para inicializar datos mock (datos de prueba) en todas las tablas principales.
Útil para desarrollo y testing cuando las tablas están vacías.
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
from models.item_label import ItemLabel
from models.inventario import Inventario
from models.factura import Factura, FacturaItem, EstadoFactura, TipoFactura
from models.receta import Receta, RecetaIngrediente, TipoReceta

def init_proveedores():
    """Inicializa proveedores de prueba."""
    print("\n1. INICIALIZANDO PROVEEDORES...")
    
    proveedores_data = [
        {
            'nombre': 'Distribuidora Alimentos S.A.',
            'ruc': '1234567890001',
            'telefono': '+593 2 234-5678',
            'email': 'ventas@distribuidora-alimentos.com',
            'direccion': 'Av. Principal 123, Quito',
            'nombre_contacto': 'Juan Pérez',
            'productos_que_provee': 'Verduras, frutas, lácteos, carnes',
            'activo': True
        },
        {
            'nombre': 'Carnicería El Buen Corte',
            'ruc': '9876543210001',
            'telefono': '+593 2 345-6789',
            'email': 'pedidos@buencorte.com',
            'direccion': 'Calle Comercial 456, Quito',
            'nombre_contacto': 'María González',
            'productos_que_provee': 'Carnes rojas, pollo, embutidos',
            'activo': True
        },
        {
            'nombre': 'Bebidas y Licores del Ecuador',
            'ruc': '1112223330001',
            'telefono': '+593 2 456-7890',
            'email': 'info@bebidas-ec.com',
            'direccion': 'Av. Industrial 789, Quito',
            'nombre_contacto': 'Carlos Rodríguez',
            'productos_que_provee': 'Bebidas gaseosas, alcohólicas, jugos',
            'activo': True
        },
        {
            'nombre': 'Suministros de Limpieza Pro',
            'ruc': '4445556660001',
            'telefono': '+593 2 567-8901',
            'email': 'contacto@limpieza-pro.com',
            'direccion': 'Calle Suministros 321, Quito',
            'nombre_contacto': 'Ana Martínez',
            'productos_que_provee': 'Artículos de limpieza, desechables',
            'activo': True
        },
        {
            'nombre': 'Panadería Artesanal',
            'ruc': '7778889990001',
            'telefono': '+593 2 678-9012',
            'email': 'pedidos@panaderia-artesanal.com',
            'direccion': 'Av. Panaderos 654, Quito',
            'nombre_contacto': 'Luis Fernández',
            'productos_que_provee': 'Pan, masas, productos de panadería',
            'activo': True
        }
    ]
    
    proveedores_creados = []
    for prov_data in proveedores_data:
        existing = Proveedor.query.filter_by(ruc=prov_data['ruc']).first()
        if not existing:
            proveedor = Proveedor(**prov_data)
            db.session.add(proveedor)
            proveedores_creados.append(proveedor)
            print(f"  ✓ Creado: {prov_data['nombre']}")
        else:
            proveedores_creados.append(existing)
            print(f"  ↻ Ya existe: {prov_data['nombre']}")
    
    db.session.commit()
    return proveedores_creados

def init_items(proveedores, labels):
    """Inicializa items de prueba."""
    print("\n2. INICIALIZANDO ITEMS...")
    
    # Mapear labels por categoría para facilitar la asignación
    labels_map = {}
    for label in labels:
        cat = label.categoria_principal
        if cat not in labels_map:
            labels_map[cat] = []
        labels_map[cat].append(label)
    
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
        
        # LÁCTEOS Y HUEVOS (8 items)
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
        
        # BEBIDAS (8 items)
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
    return items_creados

def init_inventario(items):
    """Inicializa inventario para los items."""
    print("\n3. INICIALIZANDO INVENTARIO...")
    
    inventario_creado = 0
    for item in items:
        existing = Inventario.query.filter_by(item_id=item.id).first()
        if not existing:
            # Generar cantidades aleatorias pero realistas
            cantidad_minima = Decimal('10.0')
            cantidad_actual = Decimal('50.0')  # Stock inicial generoso
            
            inventario = Inventario(
                item_id=item.id,
                ubicacion='bodega_principal',
                cantidad_actual=cantidad_actual,
                cantidad_minima=cantidad_minima,
                unidad=item.unidad,
                ultimo_costo_unitario=item.costo_unitario_actual
            )
            db.session.add(inventario)
            inventario_creado += 1
            print(f"  ✓ Inventario creado para: {item.nombre} ({cantidad_actual} {item.unidad})")
        else:
            print(f"  ↻ Ya existe inventario para: {item.nombre}")
    
    db.session.commit()
    print(f"  Total inventarios creados: {inventario_creado}")

def init_facturas(proveedores, items):
    """Inicializa 20 facturas de prueba con items relacionados."""
    print("\n4. INICIALIZANDO FACTURAS (20 FACTURAS)...")
    
    if not proveedores or not items:
        print("  ⚠ No hay proveedores o items, saltando facturas")
        return []
    
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
    print(f"  Total facturas creadas: {len(facturas_creadas)}")
    return facturas_creadas

def init_recetas(items):
    """Inicializa 12 plantillas de recetas de prueba."""
    print("\n5. INICIALIZANDO RECETAS (12 PLANTILLAS)...")
    
    if not items or len(items) < 10:
        print("  ⚠ No hay suficientes items, saltando recetas")
        return []
    
    # Crear un mapa de items por nombre para facilitar la búsqueda
    items_map = {}
    for item in items:
        items_map[item.nombre.lower()] = item
    
    def buscar_item(nombre):
        """Busca un item por nombre (case-insensitive)."""
        return items_map.get(nombre.lower())
    
    recetas_data = [
        # DESAYUNOS (4 recetas)
        {
            'nombre': 'Huevos Revueltos con Pan',
            'descripcion': 'Huevos revueltos con pan tostado y mantequilla',
            'tipo': TipoReceta.DESAYUNO.value,
            'porciones': 2,
            'tiempo_preparacion': 15,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Huevos'), 'cantidad': 0.5, 'unidad': 'docena'},
                {'item': buscar_item('Pan de Molde'), 'cantidad': 4, 'unidad': 'unidad'},
                {'item': buscar_item('Mantequilla'), 'cantidad': 0.05, 'unidad': 'kg'},
                {'item': buscar_item('Sal'), 'cantidad': 0.01, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Avena con Frutas',
            'descripcion': 'Avena cocida con fresas y plátano',
            'tipo': TipoReceta.DESAYUNO.value,
            'porciones': 2,
            'tiempo_preparacion': 20,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Avena'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Fresas'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Plátano'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Leche Entera'), 'cantidad': 0.5, 'unidad': 'litro'},
            ]
        },
        {
            'nombre': 'Tortillas con Queso',
            'descripcion': 'Tortillas de harina con queso mozzarella',
            'tipo': TipoReceta.DESAYUNO.value,
            'porciones': 4,
            'tiempo_preparacion': 25,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Tortillas'), 'cantidad': 1, 'unidad': 'paquete'},
                {'item': buscar_item('Queso Mozzarella'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Aceite de Oliva'), 'cantidad': 0.05, 'unidad': 'litro'},
            ]
        },
        {
            'nombre': 'Yogurt con Granola y Manzana',
            'descripcion': 'Yogurt natural con granola y manzana fresca',
            'tipo': TipoReceta.DESAYUNO.value,
            'porciones': 2,
            'tiempo_preparacion': 10,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Yogurt Natural'), 'cantidad': 0.5, 'unidad': 'litro'},
                {'item': buscar_item('Manzana'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Avena'), 'cantidad': 0.1, 'unidad': 'kg'},
            ]
        },
        
        # ALMUERZOS (5 recetas)
        {
            'nombre': 'Arroz con Pollo',
            'descripcion': 'Arroz con pollo, verduras y especias',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 6,
            'tiempo_preparacion': 45,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Arroz Blanco'), 'cantidad': 1.0, 'unidad': 'kg'},
                {'item': buscar_item('Pechuga de Pollo'), 'cantidad': 1.0, 'unidad': 'kg'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Tomate Fresco'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Pimiento Rojo'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.05, 'unidad': 'kg'},
                {'item': buscar_item('Comino'), 'cantidad': 0.01, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Pasta con Salsa de Tomate y Queso',
            'descripcion': 'Pasta espagueti con salsa de tomate casera y queso parmesano',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 4,
            'tiempo_preparacion': 30,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Pasta Espagueti'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Tomate Fresco'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.15, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.03, 'unidad': 'kg'},
                {'item': buscar_item('Queso Parmesano'), 'cantidad': 0.1, 'unidad': 'kg'},
                {'item': buscar_item('Aceite de Oliva'), 'cantidad': 0.05, 'unidad': 'litro'},
                {'item': buscar_item('Orégano'), 'cantidad': 0.01, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Carne de Res con Papas',
            'descripcion': 'Carne de res en trozos con papas y verduras',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 4,
            'tiempo_preparacion': 60,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Carne de Res en Trozos'), 'cantidad': 1.0, 'unidad': 'kg'},
                {'item': buscar_item('Papa'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Zanahoria'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.05, 'unidad': 'kg'},
                {'item': buscar_item('Pimienta Negra'), 'cantidad': 0.01, 'unidad': 'kg'},
                {'item': buscar_item('Sal'), 'cantidad': 0.02, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Ensalada César con Pollo',
            'descripcion': 'Ensalada fresca con pollo a la parrilla, lechuga y aderezo',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 4,
            'tiempo_preparacion': 25,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Lechuga'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Pechuga de Pollo'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Queso Parmesano'), 'cantidad': 0.05, 'unidad': 'kg'},
                {'item': buscar_item('Aceite de Oliva'), 'cantidad': 0.1, 'unidad': 'litro'},
                {'item': buscar_item('Limón'), 'cantidad': 0.1, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.02, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Frijoles con Arroz',
            'descripcion': 'Frijoles negros cocidos con arroz blanco',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 6,
            'tiempo_preparacion': 90,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Frijoles Negros'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Arroz Blanco'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.15, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.03, 'unidad': 'kg'},
                {'item': buscar_item('Comino'), 'cantidad': 0.01, 'unidad': 'kg'},
                {'item': buscar_item('Sal'), 'cantidad': 0.02, 'unidad': 'kg'},
            ]
        },
        
        # CENAS (3 recetas)
        {
            'nombre': 'Pescado a la Plancha con Verduras',
            'descripcion': 'Pescado fresco a la plancha con verduras al vapor',
            'tipo': TipoReceta.CENA.value,
            'porciones': 4,
            'tiempo_preparacion': 30,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Pescado Fresco'), 'cantidad': 1.0, 'unidad': 'kg'},
                {'item': buscar_item('Brócoli'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Zanahoria'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Limón'), 'cantidad': 0.1, 'unidad': 'kg'},
                {'item': buscar_item('Aceite de Oliva'), 'cantidad': 0.05, 'unidad': 'litro'},
                {'item': buscar_item('Pimienta Negra'), 'cantidad': 0.01, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Pasta Penne con Pollo y Crema',
            'descripcion': 'Pasta penne con pollo en salsa de crema',
            'tipo': TipoReceta.CENA.value,
            'porciones': 4,
            'tiempo_preparacion': 35,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Pasta Penne'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Pechuga de Pollo'), 'cantidad': 0.5, 'unidad': 'kg'},
                {'item': buscar_item('Crema de Leche'), 'cantidad': 0.3, 'unidad': 'litro'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.15, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.03, 'unidad': 'kg'},
                {'item': buscar_item('Queso Cheddar'), 'cantidad': 0.1, 'unidad': 'kg'},
            ]
        },
        {
            'nombre': 'Sopa de Verduras',
            'descripcion': 'Sopa casera de verduras frescas',
            'tipo': TipoReceta.CENA.value,
            'porciones': 6,
            'tiempo_preparacion': 40,
            'activa': True,
            'ingredientes': [
                {'item': buscar_item('Tomate Fresco'), 'cantidad': 0.4, 'unidad': 'kg'},
                {'item': buscar_item('Cebolla Blanca'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Zanahoria'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Papa'), 'cantidad': 0.3, 'unidad': 'kg'},
                {'item': buscar_item('Lechuga'), 'cantidad': 0.2, 'unidad': 'kg'},
                {'item': buscar_item('Ajo'), 'cantidad': 0.03, 'unidad': 'kg'},
                {'item': buscar_item('Sal'), 'cantidad': 0.02, 'unidad': 'kg'},
                {'item': buscar_item('Pimienta Negra'), 'cantidad': 0.01, 'unidad': 'kg'},
            ]
        }
    ]
    
    recetas_creadas = []
    for receta_data in recetas_data:
        # Separar ingredientes
        ingredientes = receta_data.pop('ingredientes', [])
        
        # Filtrar ingredientes que existen (no None)
        ingredientes_validos = [ing for ing in ingredientes if ing.get('item') is not None]
        
        if not ingredientes_validos:
            print(f"  ⚠ Saltando receta '{receta_data['nombre']}': no hay ingredientes válidos")
            continue
        
        existing = Receta.query.filter_by(nombre=receta_data['nombre']).first()
        if not existing:
            receta = Receta(**receta_data)
            db.session.add(receta)
            db.session.flush()  # Para obtener el ID
            
            # Crear ingredientes
            for ing_data in ingredientes_validos:
                ingrediente = RecetaIngrediente(
                    receta_id=receta.id,
                    item_id=ing_data['item'].id,
                    cantidad=Decimal(str(ing_data['cantidad'])),
                    unidad=ing_data['unidad']
                )
                db.session.add(ingrediente)
            
            # Calcular totales
            receta.calcular_totales()
            
            recetas_creadas.append(receta)
            print(f"  ✓ Creada: {receta_data['nombre']} ({len(ingredientes_validos)} ingredientes)")
        else:
            recetas_creadas.append(existing)
            print(f"  ↻ Ya existe: {receta_data['nombre']}")
    
    db.session.commit()
    return recetas_creadas

def init_mock_data():
    """Función principal para inicializar todos los datos mock."""
    print("=" * 60)
    print("INICIALIZACIÓN DE DATOS MOCK")
    print("=" * 60)
    
    # 1. Inicializar labels primero (si no existen)
    print("\n0. VERIFICANDO LABELS...")
    labels = ItemLabel.query.all()
    if not labels:
        print("  ⚠ No hay labels. Ejecuta primero: python scripts/init_food_labels.py")
        print("  Continuando sin labels...")
    else:
        print(f"  ✓ Encontradas {len(labels)} labels")
    
    # 2. Crear proveedores
    proveedores = init_proveedores()
    
    # 3. Crear items
    items = init_items(proveedores, labels)
    
    # 4. Crear inventario
    init_inventario(items)
    
    # 5. Crear facturas
    facturas = init_facturas(proveedores, items)
    
    # 6. Crear recetas
    recetas = init_recetas(items)
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print("=" * 60)
    print(f"  Proveedores: {len(proveedores)}")
    print(f"  Items: {len(items)}")
    print(f"  Facturas: {len(facturas)}")
    print(f"  Recetas: {len(recetas)}")
    print("\n✓ Inicialización de datos mock completada!")
    print("=" * 60)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_mock_data()
