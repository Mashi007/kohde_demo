"""
Script para verificar y corregir el esquema de tickets.
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
    print("VERIFICACIÓN DE ESQUEMA DE TICKETS")
    print("=" * 60)
    
    # Verificar si existe tabla clientes
    result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'clientes'"))
    tabla_clientes_existe = bool(list(result))
    print(f"\n📊 Tabla 'clientes' existe: {tabla_clientes_existe}")
    
    # Verificar restricciones de cliente_id en tickets
    result = db.session.execute(text("""
        SELECT 
            column_name, 
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'tickets' AND column_name = 'cliente_id'
    """))
    columna_info = list(result)
    if columna_info:
        print(f"\n📋 Columna cliente_id:")
        for row in columna_info:
            print(f"   - Nullable: {row[1]}")
            print(f"   - Default: {row[2]}")
    
    # Verificar foreign keys
    result = db.session.execute(text("""
        SELECT 
            constraint_name,
            constraint_type
        FROM information_schema.table_constraints 
        WHERE table_name = 'tickets' AND constraint_name LIKE '%cliente%'
    """))
    constraints = list(result)
    print(f"\n🔗 Restricciones relacionadas con cliente:")
    for row in constraints:
        print(f"   - {row[0]}: {row[1]}")
    
    # Si existe tabla clientes, crear cliente dummy con id=0
    if tabla_clientes_existe:
        print("\n🔧 Intentando crear cliente dummy con id=0...")
        try:
            # Verificar si ya existe
            result = db.session.execute(text("SELECT id FROM clientes WHERE id = 0"))
            existe = result.scalar()
            
            if not existe:
                db.session.execute(text("""
                    INSERT INTO clientes (id, nombre, tipo, ruc_ci, telefono, email, direccion, fecha_registro, activo, notas)
                    VALUES (0, 'Sistema Automático', 'OTRO', '0000000000', '0000000000', 'sistema@restaurantes.com', 'Sistema', NOW(), false, 'Cliente dummy para tickets automáticos')
                    ON CONFLICT (id) DO NOTHING
                """))
                db.session.commit()
                print("   ✅ Cliente dummy creado")
            else:
                print("   ↻ Cliente dummy ya existe")
        except Exception as e:
            print(f"   ⚠ Error: {e}")
            db.session.rollback()
    
    print("\n" + "=" * 60)
