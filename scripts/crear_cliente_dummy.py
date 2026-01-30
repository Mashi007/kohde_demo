"""
Script para crear cliente dummy con id=0 para tickets automáticos.
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
    print("CREAR CLIENTE DUMMY PARA TICKETS AUTOMÁTICOS")
    print("=" * 60)
    
    # Verificar valores del enum tipocliente
    try:
        result = db.session.execute(text("SELECT unnest(enum_range(NULL::tipocliente))::text"))
        valores_tipo = [r[0] for r in result]
        print(f"\n✅ Valores enum 'tipocliente': {valores_tipo}")
        tipo_cliente = valores_tipo[0] if valores_tipo else 'EMPRESA'
    except Exception as e:
        print(f"⚠ Error al obtener enum: {e}")
        tipo_cliente = 'EMPRESA'  # Valor por defecto
    
    # Verificar si ya existe cliente con id=0
    try:
        result = db.session.execute(text("SELECT id FROM clientes WHERE id = 0"))
        existe = result.scalar()
        
        if existe:
            print("\n✅ Cliente dummy (id=0) ya existe")
        else:
            print(f"\n🔧 Creando cliente dummy con id=0 (tipo: {tipo_cliente})...")
            db.session.execute(text(f"""
                INSERT INTO clientes (id, nombre, tipo, ruc_ci, telefono, email, direccion, fecha_registro, activo, notas)
                VALUES (0, 'Sistema Automático', '{tipo_cliente}', '0000000000', '0000000000', 'sistema@restaurantes.com', 'Sistema', NOW(), false, 'Cliente dummy para tickets automáticos')
            """))
            db.session.commit()
            print("✅ Cliente dummy creado exitosamente")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
