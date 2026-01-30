"""
Script para aplicar migraciones de Alembic.
Ejecutar: python scripts/aplicar_migracion.py
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from alembic.config import Config
from alembic import command

def aplicar_migracion():
    """Aplica las migraciones pendientes de Alembic."""
    print("=" * 70)
    print("APLICANDO MIGRACIONES DE ALEMBIC")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            alembic_cfg = Config("alembic.ini")
            
            # Mostrar estado actual
            print("📊 Estado actual de migraciones:")
            print("-" * 70)
            try:
                command.current(alembic_cfg)
            except Exception as e:
                print(f"   ⚠️  No hay migraciones aplicadas aún: {e}")
            
            print()
            print("🔄 Aplicando migraciones...")
            print("-" * 70)
            
            # Aplicar migraciones
            command.upgrade(alembic_cfg, "head")
            
            print()
            print("✅ Migración aplicada exitosamente")
            print()
            print("📋 Verificación:")
            print("-" * 70)
            command.current(alembic_cfg)
            
            print()
            print("=" * 70)
            print("✅ PROCESO COMPLETADO")
            print("=" * 70)
            
        except Exception as e:
            print()
            print("❌ Error al aplicar migración:")
            print(f"   {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    aplicar_migracion()
