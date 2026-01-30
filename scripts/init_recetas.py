"""
Script para inicializar recetas de prueba.
Requiere: Items activos
"""
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.item import Item
from models.receta import Receta, RecetaIngrediente, TipoReceta

def init_recetas():
    """Inicializa 12 plantillas de recetas de prueba."""
    print("=" * 60)
    print("INICIALIZACIÓN DE RECETAS")
    print("=" * 60)
    
    # Verificar items
    items = Item.query.filter_by(activo=True).all()
    if not items or len(items) < 10:
        print("\n⚠ No hay suficientes items activos.")
        print("  Ejecuta primero: python scripts/init_items.py")
        return []
    
    print(f"\n✓ Encontrados {len(items)} items activos")
    print("\n5. INICIALIZANDO RECETAS (12 PLANTILLAS)...")
    
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
    print(f"\n✓ Total recetas creadas/actualizadas: {len(recetas_creadas)}")
    return recetas_creadas

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        recetas = init_recetas()
        print(f"\n{'='*60}")
        print(f"✓ Proceso completado: {len(recetas)} recetas disponibles")
        print(f"{'='*60}")
