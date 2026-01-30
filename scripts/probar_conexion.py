"""
Script para probar la conexión a la base de datos.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from models import db

print("=" * 60)
print("PRUEBA DE CONEXIÓN A BASE DE DATOS")
print("=" * 60)

app = create_app()

with app.app_context():
    try:
        # Intentar conectar
        print("\n🔌 Intentando conectar a la base de datos...")
        print(f"📍 URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Oculto'}")
        
        # Probar conexión simple
        db.engine.connect()
        print("✅ Conexión exitosa!")
        
        # Probar una query simple
        print("\n🔍 Probando query simple...")
        result = db.session.execute(db.text("SELECT version();"))
        version = result.scalar()
        print(f"✅ PostgreSQL versión: {version}")
        
        # Verificar tablas
        print("\n📊 Verificando tablas existentes...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Tablas encontradas: {len(tables)}")
        if tables:
            print(f"   Primeras 5: {', '.join(tables[:5])}")
        
    except Exception as e:
        print(f"\n❌ Error de conexión:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        
        # Información adicional
        import traceback
        print("\n📋 Detalles del error:")
        print("-" * 60)
        traceback.print_exc()

print("\n" + "=" * 60)
