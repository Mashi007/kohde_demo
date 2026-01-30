"""
Script para verificar los valores de los enums en PostgreSQL.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("=" * 60)
    print("VERIFICACIÓN DE ENUMS EN POSTGRESQL")
    print("=" * 60)
    
    # Verificar estadopedido
    try:
        result = db.session.execute(text("SELECT unnest(enum_range(NULL::estadopedido))::text"))
        valores = [r[0] for r in result]
        print(f"\n✅ Enum 'estadopedido': {valores}")
    except Exception as e:
        print(f"\n❌ Error al verificar estadopedido: {e}")
    
    # Verificar estadopedidointerno
    try:
        result = db.session.execute(text("SELECT unnest(enum_range(NULL::estadopedidointerno))::text"))
        valores = [r[0] for r in result]
        print(f"✅ Enum 'estadopedidointerno': {valores}")
    except Exception as e:
        print(f"❌ Error al verificar estadopedidointerno: {e}")
    
    # Verificar tipomerma
    try:
        result = db.session.execute(text("SELECT unnest(enum_range(NULL::tipomerma))::text"))
        valores = [r[0] for r in result]
        print(f"✅ Enum 'tipomerma': {valores}")
    except Exception as e:
        print(f"❌ Error al verificar tipomerma: {e}")
    
    print("\n" + "=" * 60)
