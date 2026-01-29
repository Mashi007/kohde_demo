"""
Script para inicializar labels/clasificaciones internacionales de alimentos.
Basado en clasificaciones FAO/WHO y estándares internacionales.
"""
from models import db
from models.item_label import ItemLabel

# Clasificaciones internacionales de alimentos para recetas/menús
FOOD_LABELS = [
    # FRUTAS Y VERDURAS
    {'codigo': 'FRU_FRESH', 'nombre_es': 'Frutas Frescas', 'nombre_en': 'Fresh Fruits', 
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Frutas frescas de temporada'},
    {'codigo': 'FRU_DRIED', 'nombre_es': 'Frutas Secas', 'nombre_en': 'Dried Fruits',
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Frutas deshidratadas'},
    {'codigo': 'VEG_LEAFY', 'nombre_es': 'Verduras de Hoja', 'nombre_en': 'Leafy Vegetables',
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Espinacas, lechuga, acelgas, etc.'},
    {'codigo': 'VEG_ROOT', 'nombre_es': 'Verduras de Raíz', 'nombre_en': 'Root Vegetables',
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Zanahorias, papas, remolachas, etc.'},
    {'codigo': 'VEG_CRUCIFEROUS', 'nombre_es': 'Verduras Crucíferas', 'nombre_en': 'Cruciferous Vegetables',
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Brócoli, coliflor, repollo, etc.'},
    {'codigo': 'VEG_NIGHTshade', 'nombre_es': 'Solanáceas', 'nombre_en': 'Nightshades',
     'categoria_principal': 'Frutas y Verduras', 'descripcion': 'Tomates, pimientos, berenjenas, etc.'},
    
    # CEREALES Y GRANOS
    {'codigo': 'GRAIN_WHEAT', 'nombre_es': 'Trigo', 'nombre_en': 'Wheat',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Trigo y derivados'},
    {'codigo': 'GRAIN_RICE', 'nombre_es': 'Arroz', 'nombre_en': 'Rice',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Arroz blanco, integral, salvaje'},
    {'codigo': 'GRAIN_CORN', 'nombre_es': 'Maíz', 'nombre_en': 'Corn',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Maíz y derivados'},
    {'codigo': 'GRAIN_OATS', 'nombre_es': 'Avena', 'nombre_en': 'Oats',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Avena y productos de avena'},
    {'codigo': 'GRAIN_QUINOA', 'nombre_es': 'Quinoa', 'nombre_en': 'Quinoa',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Quinoa y pseudocereales'},
    {'codigo': 'GRAIN_LEGUMES', 'nombre_es': 'Legumbres', 'nombre_en': 'Legumes',
     'categoria_principal': 'Cereales y Granos', 'descripcion': 'Frijoles, lentejas, garbanzos, etc.'},
    
    # PROTEÍNAS
    {'codigo': 'PROT_BEEF', 'nombre_es': 'Carne de Res', 'nombre_en': 'Beef',
     'categoria_principal': 'Proteínas', 'descripcion': 'Carne de res y ternera'},
    {'codigo': 'PROT_PORK', 'nombre_es': 'Cerdo', 'nombre_en': 'Pork',
     'categoria_principal': 'Proteínas', 'descripcion': 'Carne de cerdo'},
    {'codigo': 'PROT_POULTRY', 'nombre_es': 'Aves', 'nombre_en': 'Poultry',
     'categoria_principal': 'Proteínas', 'descripcion': 'Pollo, pavo, pato, etc.'},
    {'codigo': 'PROT_FISH', 'nombre_es': 'Pescado', 'nombre_en': 'Fish',
     'categoria_principal': 'Proteínas', 'descripcion': 'Pescados frescos'},
    {'codigo': 'PROT_SEAFOOD', 'nombre_es': 'Mariscos', 'nombre_en': 'Seafood',
     'categoria_principal': 'Proteínas', 'descripcion': 'Camarones, langostinos, pulpo, etc.'},
    {'codigo': 'PROT_EGGS', 'nombre_es': 'Huevos', 'nombre_en': 'Eggs',
     'categoria_principal': 'Proteínas', 'descripcion': 'Huevos de gallina y otras aves'},
    {'codigo': 'PROT_PLANT', 'nombre_es': 'Proteína Vegetal', 'nombre_en': 'Plant Protein',
     'categoria_principal': 'Proteínas', 'descripcion': 'Tofu, tempeh, seitán, etc.'},
    
    # LÁCTEOS
    {'codigo': 'DAIRY_MILK', 'nombre_es': 'Leche', 'nombre_en': 'Milk',
     'categoria_principal': 'Lácteos', 'descripcion': 'Leche de vaca, cabra, etc.'},
    {'codigo': 'DAIRY_CHEESE', 'nombre_es': 'Queso', 'nombre_en': 'Cheese',
     'categoria_principal': 'Lácteos', 'descripcion': 'Quesos diversos'},
    {'codigo': 'DAIRY_YOGURT', 'nombre_es': 'Yogurt', 'nombre_en': 'Yogurt',
     'categoria_principal': 'Lácteos', 'descripcion': 'Yogurt natural y saborizado'},
    {'codigo': 'DAIRY_CREAM', 'nombre_es': 'Crema', 'nombre_en': 'Cream',
     'categoria_principal': 'Lácteos', 'descripcion': 'Crema de leche, nata'},
    {'codigo': 'DAIRY_BUTTER', 'nombre_es': 'Mantequilla', 'nombre_en': 'Butter',
     'categoria_principal': 'Lácteos', 'descripcion': 'Mantequilla y margarina'},
    
    # GRASAS Y ACEITES
    {'codigo': 'FAT_OIL_OLIVE', 'nombre_es': 'Aceite de Oliva', 'nombre_en': 'Olive Oil',
     'categoria_principal': 'Grasas y Aceites', 'descripcion': 'Aceite de oliva extra virgen y refinado'},
    {'codigo': 'FAT_OIL_VEGETABLE', 'nombre_es': 'Aceite Vegetal', 'nombre_en': 'Vegetable Oil',
     'categoria_principal': 'Grasas y Aceites', 'descripcion': 'Aceites vegetales diversos'},
    {'codigo': 'FAT_NUTS', 'nombre_es': 'Frutos Secos', 'nombre_en': 'Nuts',
     'categoria_principal': 'Grasas y Aceites', 'descripcion': 'Almendras, nueces, avellanas, etc.'},
    {'codigo': 'FAT_SEEDS', 'nombre_es': 'Semillas', 'nombre_en': 'Seeds',
     'categoria_principal': 'Grasas y Aceites', 'descripcion': 'Semillas de girasol, chía, sésamo, etc.'},
    
    # ESPECIAS Y CONDIMENTOS
    {'codigo': 'SPICE_SALT', 'nombre_es': 'Sal', 'nombre_en': 'Salt',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Sal de mesa y sales especiales'},
    {'codigo': 'SPICE_PEPPER', 'nombre_es': 'Pimienta', 'nombre_en': 'Pepper',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Pimienta negra, blanca, rosa'},
    {'codigo': 'SPICE_HERBS', 'nombre_es': 'Hierbas', 'nombre_en': 'Herbs',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Albahaca, orégano, romero, etc.'},
    {'codigo': 'SPICE_SPICES', 'nombre_es': 'Especias', 'nombre_en': 'Spices',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Canela, clavo, comino, etc.'},
    {'codigo': 'SPICE_GARLIC', 'nombre_es': 'Ajo', 'nombre_en': 'Garlic',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Ajo fresco y en polvo'},
    {'codigo': 'SPICE_ONION', 'nombre_es': 'Cebolla', 'nombre_en': 'Onion',
     'categoria_principal': 'Especias y Condimentos', 'descripcion': 'Cebolla blanca, morada, verde'},
    
    # BEBIDAS
    {'codigo': 'BEV_WATER', 'nombre_es': 'Agua', 'nombre_en': 'Water',
     'categoria_principal': 'Bebidas', 'descripcion': 'Agua natural y mineral'},
    {'codigo': 'BEV_JUICE', 'nombre_es': 'Jugos', 'nombre_en': 'Juice',
     'categoria_principal': 'Bebidas', 'descripcion': 'Jugos naturales y procesados'},
    {'codigo': 'BEV_SOFT', 'nombre_es': 'Refrescos', 'nombre_en': 'Soft Drinks',
     'categoria_principal': 'Bebidas', 'descripcion': 'Bebidas gaseosas'},
    {'codigo': 'BEV_ALCOHOL', 'nombre_es': 'Alcohol', 'nombre_en': 'Alcohol',
     'categoria_principal': 'Bebidas', 'descripcion': 'Vino, cerveza, licores'},
    {'codigo': 'BEV_TEA', 'nombre_es': 'Té', 'nombre_en': 'Tea',
     'categoria_principal': 'Bebidas', 'descripcion': 'Té verde, negro, herbal'},
    {'codigo': 'BEV_COFFEE', 'nombre_es': 'Café', 'nombre_en': 'Coffee',
     'categoria_principal': 'Bebidas', 'descripcion': 'Café molido, granos, instantáneo'},
    
    # OTROS
    {'codigo': 'OTHER_SUGAR', 'nombre_es': 'Azúcar', 'nombre_en': 'Sugar',
     'categoria_principal': 'Otros', 'descripcion': 'Azúcar blanco, moreno, miel'},
    {'codigo': 'OTHER_VINEGAR', 'nombre_es': 'Vinagre', 'nombre_en': 'Vinegar',
     'categoria_principal': 'Otros', 'descripcion': 'Vinagre de vino, manzana, balsámico'},
    {'codigo': 'OTHER_FLOUR', 'nombre_es': 'Harina', 'nombre_en': 'Flour',
     'categoria_principal': 'Otros', 'descripcion': 'Harinas diversas'},
    {'codigo': 'OTHER_PASTA', 'nombre_es': 'Pasta', 'nombre_en': 'Pasta',
     'categoria_principal': 'Otros', 'descripcion': 'Pastas secas y frescas'},
    {'codigo': 'OTHER_BREAD', 'nombre_es': 'Pan', 'nombre_en': 'Bread',
     'categoria_principal': 'Otros', 'descripcion': 'Pan blanco, integral, artesanal'},
]

def init_food_labels():
    """Inicializa las labels de alimentos en la base de datos."""
    print("Inicializando labels de alimentos internacionales...")
    
    for label_data in FOOD_LABELS:
        # Verificar si ya existe
        existing = ItemLabel.query.filter_by(codigo=label_data['codigo']).first()
        if not existing:
            label = ItemLabel(**label_data)
            db.session.add(label)
            print(f"  ✓ Agregado: {label_data['nombre_es']} ({label_data['codigo']})")
        else:
            print(f"  - Ya existe: {label_data['nombre_es']} ({label_data['codigo']})")
    
    db.session.commit()
    print(f"\n✓ Proceso completado. Total de labels: {len(FOOD_LABELS)}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        init_food_labels()
