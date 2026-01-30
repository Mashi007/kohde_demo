"""
Script temporal para agregar columnas faltantes a la base de datos.
"""
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

app = create_app()
with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Agregar columnas faltantes si no existen
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN IF NOT EXISTS nombre_contacto VARCHAR(200)"))
            conn.execute(text("ALTER TABLE proveedores ADD COLUMN IF NOT EXISTS productos_que_provee TEXT"))
            # Si dias_credito no existe y es NOT NULL, hacerla nullable primero o agregar con default
            try:
                conn.execute(text("ALTER TABLE proveedores ADD COLUMN IF NOT EXISTS dias_credito INTEGER DEFAULT 30"))
                conn.execute(text("ALTER TABLE proveedores ALTER COLUMN dias_credito SET DEFAULT 30"))
                conn.execute(text("UPDATE proveedores SET dias_credito = 30 WHERE dias_credito IS NULL"))
            except:
                pass  # Si ya existe o hay error, continuar
            conn.commit()
        print("✓ Columnas agregadas correctamente")
    except Exception as e:
        print(f"⚠ Error: {e}")
        # Si la columna ya existe, está bien
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print("  (Las columnas ya existen, continuando...)")
        else:
            raise
