"""
Script maestro para inicializar todos los datos necesarios.
Ejecuta primero las labels y luego los datos mock.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def init_all():
    """Inicializa todos los datos necesarios."""
    print("=" * 60)
    print("INICIALIZACIÓN COMPLETA DE DATOS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # 1. Inicializar labels primero
        print("\n" + "=" * 60)
        print("PASO 1: Inicializando Labels de Alimentos")
        print("=" * 60)
        try:
            from scripts.init_food_labels import init_food_labels
            init_food_labels()
        except Exception as e:
            print(f"  ⚠ Error inicializando labels: {str(e)}")
            print("  Continuando con datos mock...")
        
        # 2. Inicializar datos mock
        print("\n" + "=" * 60)
        print("PASO 2: Inicializando Datos Mock")
        print("=" * 60)
        try:
            from scripts.init_mock_data import init_mock_data
            init_mock_data()
        except Exception as e:
            print(f"  ✗ Error inicializando datos mock: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "=" * 60)
    print("✓ INICIALIZACIÓN COMPLETA EXITOSA")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = init_all()
    sys.exit(0 if success else 1)
