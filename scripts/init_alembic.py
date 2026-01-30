"""
Script para inicializar Alembic en el proyecto si no está configurado.
Ejecutar: python scripts/init_alembic.py
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def init_alembic():
    """Inicializa Alembic si no está configurado."""
    project_root = Path(__file__).parent.parent
    alembic_dir = project_root / 'alembic'
    alembic_ini = project_root / 'alembic.ini'
    
    print("=" * 70)
    print("INICIALIZACIÓN DE ALEMBIC")
    print("=" * 70)
    print()
    
    # Verificar si ya existe
    if alembic_dir.exists() and alembic_ini.exists():
        print("✅ Alembic ya está inicializado")
        print(f"   Directorio: {alembic_dir}")
        print(f"   Config: {alembic_ini}")
        print()
        print("Para crear una migración inicial:")
        print("  alembic revision --autogenerate -m 'Migración inicial'")
        return
    
    print("⚠️  Alembic no está inicializado")
    print()
    print("Para inicializar Alembic, ejecuta:")
    print("  alembic init alembic")
    print()
    print("Luego configura:")
    print("  1. Edita alembic/env.py para usar Config.SQLALCHEMY_DATABASE_URI")
    print("  2. Importa todos los modelos en alembic/env.py")
    print("  3. Crea la primera migración: alembic revision --autogenerate -m 'Migración inicial'")
    print("  4. Aplica: alembic upgrade head")
    print()
    print("Ver MIGRACIONES_ALEMBIC.md para más detalles.")

if __name__ == '__main__':
    init_alembic()
