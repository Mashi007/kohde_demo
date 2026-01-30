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
    """Inicializa facturas de prueba con items."""
    print("\n4. INICIALIZANDO FACTURAS...")
    
    if not proveedores or not items:
        print("  ⚠ No hay proveedores o items, saltando facturas")
        return []
    
    # Crear algunas facturas aprobadas para poder calcular costos promedio
    facturas_data = [
        {
            'numero_factura': 'FAC-2024-001',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': proveedores[0].id,
            'fecha_emision': datetime.now() - timedelta(days=30),
            'fecha_recepcion': datetime.now() - timedelta(days=29),
            'subtotal': Decimal('150.00'),
            'iva': Decimal('18.00'),
            'total': Decimal('168.00'),
            'estado': EstadoFactura.APROBADA,
            'aprobado_por': 1,
            'fecha_aprobacion': datetime.now() - timedelta(days=28),
            'items': [
                {'item_id': items[0].id, 'cantidad': 50, 'precio_unitario': 1.50, 'cantidad_aprobada': 50},
                {'item_id': items[1].id, 'cantidad': 30, 'precio_unitario': 2.00, 'cantidad_aprobada': 30},
                {'item_id': items[2].id, 'cantidad': 100, 'precio_unitario': 0.80, 'cantidad_aprobada': 100},
            ]
        },
        {
            'numero_factura': 'FAC-2024-002',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': proveedores[1].id,
            'fecha_emision': datetime.now() - timedelta(days=20),
            'fecha_recepcion': datetime.now() - timedelta(days=19),
            'subtotal': Decimal('200.00'),
            'iva': Decimal('24.00'),
            'total': Decimal('224.00'),
            'estado': EstadoFactura.APROBADA,
            'aprobado_por': 1,
            'fecha_aprobacion': datetime.now() - timedelta(days=18),
            'items': [
                {'item_id': items[3].id, 'cantidad': 20, 'precio_unitario': 5.50, 'cantidad_aprobada': 20},
                {'item_id': items[4].id, 'cantidad': 15, 'precio_unitario': 8.00, 'cantidad_aprobada': 15},
            ]
        },
        {
            'numero_factura': 'FAC-2024-003',
            'tipo': TipoFactura.PROVEEDOR,
            'proveedor_id': proveedores[0].id,
            'fecha_emision': datetime.now() - timedelta(days=10),
            'fecha_recepcion': datetime.now() - timedelta(days=9),
            'subtotal': Decimal('120.00'),
            'iva': Decimal('14.40'),
            'total': Decimal('134.40'),
            'estado': EstadoFactura.APROBADA,
            'aprobado_por': 1,
            'fecha_aprobacion': datetime.now() - timedelta(days=8),
            'items': [
                {'item_id': items[0].id, 'cantidad': 40, 'precio_unitario': 1.45, 'cantidad_aprobada': 40},
                {'item_id': items[6].id, 'cantidad': 20, 'precio_unitario': 1.20, 'cantidad_aprobada': 20},
                {'item_id': items[7].id, 'cantidad': 10, 'precio_unitario': 6.50, 'cantidad_aprobada': 10},
            ]
        }
    ]
    
    facturas_creadas = []
    for fact_data in facturas_data:
        # Separar items de la factura
        items_factura = fact_data.pop('items', [])
        
        existing = Factura.query.filter_by(numero_factura=fact_data['numero_factura']).first()
        if not existing:
            factura = Factura(**fact_data)
            db.session.add(factura)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de la factura
            for item_fact in items_factura:
                cantidad = Decimal(str(item_fact['cantidad']))
                precio_unitario = Decimal(str(item_fact['precio_unitario']))
                subtotal = cantidad * precio_unitario
                
                factura_item = FacturaItem(
                    factura_id=factura.id,
                    item_id=item_fact['item_id'],
                    cantidad_facturada=cantidad,
                    cantidad_aprobada=Decimal(str(item_fact['cantidad_aprobada'])),
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                    unidad=items[0].unidad if items else 'unidad'
                )
                db.session.add(factura_item)
            
            facturas_creadas.append(factura)
            print(f"  ✓ Creada: {fact_data['numero_factura']} - ${fact_data['total']}")
        else:
            facturas_creadas.append(existing)
            print(f"  ↻ Ya existe: {fact_data['numero_factura']}")
    
    db.session.commit()
    return facturas_creadas

def init_recetas(items):
    """Inicializa recetas de prueba."""
    print("\n5. INICIALIZANDO RECETAS...")
    
    if not items or len(items) < 5:
        print("  ⚠ No hay suficientes items, saltando recetas")
        return []
    
    recetas_data = [
        {
            'nombre': 'Pasta con Salsa de Tomate',
            'descripcion': 'Pasta con salsa de tomate y queso',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 4,
            'tiempo_preparacion': 30,
            'activa': True,
            'ingredientes': [
                {'item_id': items[8].id, 'cantidad': 0.5, 'unidad': 'kg'},  # Pasta
                {'item_id': items[1].id, 'cantidad': 0.5, 'unidad': 'kg'},  # Tomate
                {'item_id': items[0].id, 'cantidad': 0.1, 'unidad': 'kg'},  # Cebolla
                {'item_id': items[7].id, 'cantidad': 0.2, 'unidad': 'kg'},  # Queso
            ]
        },
        {
            'nombre': 'Arroz con Pollo',
            'descripcion': 'Arroz con pollo y verduras',
            'tipo': TipoReceta.ALMUERZO.value,
            'porciones': 6,
            'tiempo_preparacion': 45,
            'activa': True,
            'ingredientes': [
                {'item_id': items[7].id, 'cantidad': 1.0, 'unidad': 'kg'},  # Arroz
                {'item_id': items[3].id, 'cantidad': 1.0, 'unidad': 'kg'},  # Pollo
                {'item_id': items[0].id, 'cantidad': 0.2, 'unidad': 'kg'},  # Cebolla
                {'item_id': items[2].id, 'cantidad': 0.3, 'unidad': 'kg'},  # Papa
            ]
        }
    ]
    
    recetas_creadas = []
    for receta_data in recetas_data:
        # Separar ingredientes
        ingredientes = receta_data.pop('ingredientes', [])
        
        existing = Receta.query.filter_by(nombre=receta_data['nombre']).first()
        if not existing:
            receta = Receta(**receta_data)
            db.session.add(receta)
            db.session.flush()  # Para obtener el ID
            
            # Crear ingredientes
            for ing_data in ingredientes:
                ingrediente = RecetaIngrediente(
                    receta_id=receta.id,
                    item_id=ing_data['item_id'],
                    cantidad=Decimal(str(ing_data['cantidad'])),
                    unidad=ing_data['unidad']
                )
                db.session.add(ingrediente)
            
            # Calcular totales
            receta.calcular_totales()
            
            recetas_creadas.append(receta)
            print(f"  ✓ Creada: {receta_data['nombre']}")
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
