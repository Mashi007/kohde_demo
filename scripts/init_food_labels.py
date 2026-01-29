"""
Script para inicializar labels/clasificaciones de alimentos.
Clasificación simplificada para restaurantes.
"""
from models import db
from models.item_label import ItemLabel

# Clasificaciones de alimentos para restaurantes
FOOD_LABELS = [
    # VERDURAS Y HORTALIZAS
    {'codigo': 'VEG_CEBOLLA', 'nombre_es': 'Cebolla', 'nombre_en': 'Onion',
     'categoria_principal': 'Verduras y hortalizas', 'descripcion': 'Cebolla blanca, morada, verde'},
    {'codigo': 'VEG_TOMATE', 'nombre_es': 'Tomate', 'nombre_en': 'Tomato',
     'categoria_principal': 'Verduras y hortalizas', 'descripcion': 'Tomate fresco'},
    {'codigo': 'VEG_ZANAHORIA', 'nombre_es': 'Zanahoria', 'nombre_en': 'Carrot',
     'categoria_principal': 'Verduras y hortalizas', 'descripcion': 'Zanahoria fresca'},
    {'codigo': 'VEG_LECHUGA', 'nombre_es': 'Lechuga', 'nombre_en': 'Lettuce',
     'categoria_principal': 'Verduras y hortalizas', 'descripcion': 'Lechuga, espinaca, acelga'},
    {'codigo': 'VEG_PAPA', 'nombre_es': 'Papa', 'nombre_en': 'Potato',
     'categoria_principal': 'Verduras y hortalizas', 'descripcion': 'Papa, camote, yuca'},
    
    # FRUTAS
    {'codigo': 'FRU_LIMON', 'nombre_es': 'Limón', 'nombre_en': 'Lemon',
     'categoria_principal': 'Frutas', 'descripcion': 'Limón, lima'},
    {'codigo': 'FRU_PLATANO', 'nombre_es': 'Plátano', 'nombre_en': 'Banana',
     'categoria_principal': 'Frutas', 'descripcion': 'Plátano, banano'},
    {'codigo': 'FRU_MANZANA', 'nombre_es': 'Manzana', 'nombre_en': 'Apple',
     'categoria_principal': 'Frutas', 'descripcion': 'Manzana'},
    {'codigo': 'FRU_FRESAS', 'nombre_es': 'Fresas', 'nombre_en': 'Strawberries',
     'categoria_principal': 'Frutas', 'descripcion': 'Fresas, frutos rojos'},
    
    # CARNES ROJAS
    {'codigo': 'CARNE_RES', 'nombre_es': 'Res', 'nombre_en': 'Beef',
     'categoria_principal': 'Carnes rojas', 'descripcion': 'Carne de res'},
    {'codigo': 'CARNE_CERDO', 'nombre_es': 'Cerdo', 'nombre_en': 'Pork',
     'categoria_principal': 'Carnes rojas', 'descripcion': 'Carne de cerdo'},
    {'codigo': 'CARNE_TERNERA', 'nombre_es': 'Ternera', 'nombre_en': 'Veal',
     'categoria_principal': 'Carnes rojas', 'descripcion': 'Carne de ternera'},
    
    # AVES Y POLLO
    {'codigo': 'AVE_POLLO', 'nombre_es': 'Pollo', 'nombre_en': 'Chicken',
     'categoria_principal': 'Aves y pollo', 'descripcion': 'Pollo entero, pechuga, muslo'},
    
    # PESCADOS Y MARISCOS
    {'codigo': 'PESCADO_FRESCO', 'nombre_es': 'Pescado', 'nombre_en': 'Fish',
     'categoria_principal': 'Pescados y mariscos', 'descripcion': 'Pescados frescos'},
    {'codigo': 'MARISCO_CAMARON', 'nombre_es': 'Mariscos', 'nombre_en': 'Seafood',
     'categoria_principal': 'Pescados y mariscos', 'descripcion': 'Camarones, langostinos, pulpo, calamar, mejillones'},
    
    # PROTEÍNAS ALTERNATIVAS
    {'codigo': 'PROT_TOFU', 'nombre_es': 'Tofu', 'nombre_en': 'Tofu',
     'categoria_principal': 'Proteínas alternativas', 'descripcion': 'Tofu'},
    {'codigo': 'PROT_SEITAN', 'nombre_es': 'Seitán', 'nombre_en': 'Seitan',
     'categoria_principal': 'Proteínas alternativas', 'descripcion': 'Seitán'},
    {'codigo': 'PROT_HAMBURGUESAS_VEG', 'nombre_es': 'Hamburguesas Vegetales', 'nombre_en': 'Vegetarian Burgers',
     'categoria_principal': 'Proteínas alternativas', 'descripcion': 'Hamburguesas vegetales'},
    
    # LÁCTEOS Y HUEVOS
    {'codigo': 'LACTEO_LECHE', 'nombre_es': 'Leche', 'nombre_en': 'Milk',
     'categoria_principal': 'Lácteos y huevos', 'descripcion': 'Leche de vaca, cabra'},
    {'codigo': 'LACTEO_QUESO', 'nombre_es': 'Queso', 'nombre_en': 'Cheese',
     'categoria_principal': 'Lácteos y huevos', 'descripcion': 'Quesos diversos'},
    {'codigo': 'LACTEO_CREMA', 'nombre_es': 'Crema', 'nombre_en': 'Cream',
     'categoria_principal': 'Lácteos y huevos', 'descripcion': 'Crema de leche, nata'},
    {'codigo': 'LACTEO_HUEVOS', 'nombre_es': 'Huevos', 'nombre_en': 'Eggs',
     'categoria_principal': 'Lácteos y huevos', 'descripcion': 'Huevos de gallina'},
    {'codigo': 'LACTEO_MANTEQUILLA', 'nombre_es': 'Mantequilla', 'nombre_en': 'Butter',
     'categoria_principal': 'Lácteos y huevos', 'descripcion': 'Mantequilla, margarina'},
    
    # PRODUCTOS SECOS Y GRANOS
    {'codigo': 'SECO_ARROZ', 'nombre_es': 'Arroz', 'nombre_en': 'Rice',
     'categoria_principal': 'Productos secos y granos', 'descripcion': 'Arroz blanco, integral'},
    {'codigo': 'SECO_PASTA', 'nombre_es': 'Pasta', 'nombre_en': 'Pasta',
     'categoria_principal': 'Productos secos y granos', 'descripcion': 'Pastas secas'},
    {'codigo': 'SECO_HARINA', 'nombre_es': 'Harina', 'nombre_en': 'Flour',
     'categoria_principal': 'Productos secos y granos', 'descripcion': 'Harinas diversas'},
    {'codigo': 'SECO_AZUCAR', 'nombre_es': 'Azúcar', 'nombre_en': 'Sugar',
     'categoria_principal': 'Productos secos y granos', 'descripcion': 'Azúcar blanco, moreno'},
    {'codigo': 'SECO_LEGUMBRES', 'nombre_es': 'Legumbres', 'nombre_en': 'Legumes',
     'categoria_principal': 'Productos secos y granos', 'descripcion': 'Frijoles, lentejas, garbanzos'},
    
    # CONDIMENTOS Y ESPECIAS
    {'codigo': 'COND_SAL', 'nombre_es': 'Sal', 'nombre_en': 'Salt',
     'categoria_principal': 'Condimentos y especias', 'descripcion': 'Sal de mesa'},
    {'codigo': 'COND_PIMIENTA', 'nombre_es': 'Pimienta', 'nombre_en': 'Pepper',
     'categoria_principal': 'Condimentos y especias', 'descripcion': 'Pimienta negra, blanca'},
    {'codigo': 'COND_AJO_POLVO', 'nombre_es': 'Ajo en Polvo', 'nombre_en': 'Garlic Powder',
     'categoria_principal': 'Condimentos y especias', 'descripcion': 'Ajo en polvo'},
    {'codigo': 'COND_COMINO', 'nombre_es': 'Comino', 'nombre_en': 'Cumin',
     'categoria_principal': 'Condimentos y especias', 'descripcion': 'Comino'},
    {'codigo': 'COND_HIERBAS', 'nombre_es': 'Hierbas Secas', 'nombre_en': 'Dried Herbs',
     'categoria_principal': 'Condimentos y especias', 'descripcion': 'Orégano, albahaca, romero, etc.'},
    
    # SALSAS Y ENVASADOS
    {'codigo': 'SALSA_KETCHUP', 'nombre_es': 'Ketchup', 'nombre_en': 'Ketchup',
     'categoria_principal': 'Salsas y envasados', 'descripcion': 'Ketchup'},
    {'codigo': 'SALSA_MAYONESA', 'nombre_es': 'Mayonesa', 'nombre_en': 'Mayonnaise',
     'categoria_principal': 'Salsas y envasados', 'descripcion': 'Mayonesa'},
    {'codigo': 'SALSA_ACEITE', 'nombre_es': 'Aceite', 'nombre_en': 'Oil',
     'categoria_principal': 'Salsas y envasados', 'descripcion': 'Aceite de oliva, vegetal'},
    {'codigo': 'SALSA_VINAGRE', 'nombre_es': 'Vinagre', 'nombre_en': 'Vinegar',
     'categoria_principal': 'Salsas y envasados', 'descripcion': 'Vinagre'},
    {'codigo': 'SALSA_PREPARADAS', 'nombre_es': 'Salsas Preparadas', 'nombre_en': 'Prepared Sauces',
     'categoria_principal': 'Salsas y envasados', 'descripcion': 'Otras salsas preparadas'},
    
    # BEBIDAS GASEOSAS
    {'codigo': 'BEB_COLA', 'nombre_es': 'Cola', 'nombre_en': 'Cola',
     'categoria_principal': 'Bebidas gaseosas', 'descripcion': 'Coca Cola, Pepsi'},
    {'codigo': 'BEB_SPRITE', 'nombre_es': 'Sprite', 'nombre_en': 'Sprite',
     'categoria_principal': 'Bebidas gaseosas', 'descripcion': 'Sprite, 7UP'},
    {'codigo': 'BEB_GINGER', 'nombre_es': 'Ginger Ale', 'nombre_en': 'Ginger Ale',
     'categoria_principal': 'Bebidas gaseosas', 'descripcion': 'Ginger Ale'},
    
    # BEBIDAS NO ALCOHÓLICAS
    {'codigo': 'BEB_JUGO', 'nombre_es': 'Jugos', 'nombre_en': 'Juice',
     'categoria_principal': 'Bebidas no alcohólicas', 'descripcion': 'Jugos naturales y procesados'},
    {'codigo': 'BEB_AGUA', 'nombre_es': 'Agua', 'nombre_en': 'Water',
     'categoria_principal': 'Bebidas no alcohólicas', 'descripcion': 'Agua natural y mineral'},
    {'codigo': 'BEB_ENERGIZANTE', 'nombre_es': 'Energizantes', 'nombre_en': 'Energy Drinks',
     'categoria_principal': 'Bebidas no alcohólicas', 'descripcion': 'Bebidas energizantes'},
    {'codigo': 'BEB_CAFE', 'nombre_es': 'Café', 'nombre_en': 'Coffee',
     'categoria_principal': 'Bebidas no alcohólicas', 'descripcion': 'Café molido, granos'},
    {'codigo': 'BEB_TE', 'nombre_es': 'Té', 'nombre_en': 'Tea',
     'categoria_principal': 'Bebidas no alcohólicas', 'descripcion': 'Té verde, negro, herbal'},
    
    # BEBIDAS ALCOHÓLICAS
    {'codigo': 'BEB_CERVEZA', 'nombre_es': 'Cerveza', 'nombre_en': 'Beer',
     'categoria_principal': 'Bebidas alcohólicas', 'descripcion': 'Cerveza'},
    {'codigo': 'BEB_VINO', 'nombre_es': 'Vino', 'nombre_en': 'Wine',
     'categoria_principal': 'Bebidas alcohólicas', 'descripcion': 'Vino tinto, blanco'},
    {'codigo': 'BEB_LICORES', 'nombre_es': 'Licores', 'nombre_en': 'Spirits',
     'categoria_principal': 'Bebidas alcohólicas', 'descripcion': 'Licores, destilados'},
    
    # PANADERÍA Y REPOSTERÍA
    {'codigo': 'PAN_PAN', 'nombre_es': 'Pan', 'nombre_en': 'Bread',
     'categoria_principal': 'Panadería y repostería', 'descripcion': 'Pan blanco, integral'},
    {'codigo': 'PAN_TORTILLAS', 'nombre_es': 'Tortillas', 'nombre_en': 'Tortillas',
     'categoria_principal': 'Panadería y repostería', 'descripcion': 'Tortillas'},
    {'codigo': 'PAN_MASAS', 'nombre_es': 'Masas', 'nombre_en': 'Dough',
     'categoria_principal': 'Panadería y repostería', 'descripcion': 'Masas para pan, pizza'},
    {'codigo': 'PAN_LEVADURA', 'nombre_es': 'Levadura', 'nombre_en': 'Yeast',
     'categoria_principal': 'Panadería y repostería', 'descripcion': 'Levadura'},
    
    # CONGELADOS
    {'codigo': 'CONG_PAPAS', 'nombre_es': 'Papas Fritas', 'nombre_en': 'Frozen Fries',
     'categoria_principal': 'Congelados', 'descripcion': 'Papas fritas congeladas'},
    {'codigo': 'CONG_VEGETALES', 'nombre_es': 'Vegetales Congelados', 'nombre_en': 'Frozen Vegetables',
     'categoria_principal': 'Congelados', 'descripcion': 'Vegetales congelados'},
    {'codigo': 'CONG_HELADOS', 'nombre_es': 'Helados', 'nombre_en': 'Ice Cream',
     'categoria_principal': 'Congelados', 'descripcion': 'Helados'},
    
    # ARTÍCULOS DE LIMPIEZA Y DESECHABLES
    {'codigo': 'LIMP_DETERGENTE', 'nombre_es': 'Detergentes', 'nombre_en': 'Detergents',
     'categoria_principal': 'Artículos de limpieza y desechables', 'descripcion': 'Detergentes'},
    {'codigo': 'LIMP_SERVILLETAS', 'nombre_es': 'Servilletas', 'nombre_en': 'Napkins',
     'categoria_principal': 'Artículos de limpieza y desechables', 'descripcion': 'Servilletas'},
    {'codigo': 'LIMP_GUANTES', 'nombre_es': 'Guantes', 'nombre_en': 'Gloves',
     'categoria_principal': 'Artículos de limpieza y desechables', 'descripcion': 'Guantes desechables'},
    {'codigo': 'LIMP_BOLSAS', 'nombre_es': 'Bolsas', 'nombre_en': 'Bags',
     'categoria_principal': 'Artículos de limpieza y desechables', 'descripcion': 'Bolsas desechables'},
    
    # OTROS / SUMINISTROS MENORES
    {'codigo': 'OTRO_PAJITAS', 'nombre_es': 'Pajitas', 'nombre_en': 'Straws',
     'categoria_principal': 'Otros / suministros menores', 'descripcion': 'Pajitas desechables'},
    {'codigo': 'OTRO_VASOS', 'nombre_es': 'Vasos Desechables', 'nombre_en': 'Disposable Cups',
     'categoria_principal': 'Otros / suministros menores', 'descripcion': 'Vasos desechables'},
    {'codigo': 'OTRO_DECORACION', 'nombre_es': 'Decoración Comestible', 'nombre_en': 'Edible Decoration',
     'categoria_principal': 'Otros / suministros menores', 'descripcion': 'Decoración comestible'},
]

def init_food_labels():
    """Inicializa las labels de alimentos en la base de datos."""
    print("Inicializando labels de alimentos para restaurantes...")
    
    for label_data in FOOD_LABELS:
        # Verificar si ya existe
        existing = ItemLabel.query.filter_by(codigo=label_data['codigo']).first()
        if not existing:
            label = ItemLabel(**label_data)
            db.session.add(label)
            print(f"  ✓ Agregado: {label_data['nombre_es']} ({label_data['codigo']})")
        else:
            # Actualizar si existe pero con diferente categoría
            existing.categoria_principal = label_data['categoria_principal']
            existing.nombre_es = label_data['nombre_es']
            existing.nombre_en = label_data['nombre_en']
            existing.descripcion = label_data['descripcion']
            print(f"  ↻ Actualizado: {label_data['nombre_es']} ({label_data['codigo']})")
    
    db.session.commit()
    print(f"\n✓ Proceso completado. Total de labels: {len(FOOD_LABELS)}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        init_food_labels()
