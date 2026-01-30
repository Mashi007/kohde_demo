"""
Script para verificar el estado de la tabla recetas y el enum tiporeceta en la BD.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import Config

def verificar_recetas():
    """Verifica el estado de la tabla recetas y el enum tiporeceta."""
    
    # Crear conexión a la base de datos
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=" * 80)
        print("VERIFICACIÓN DE RECETAS EN BASE DE DATOS")
        print("=" * 80)
        print()
        
        # 1. Verificar valores del enum tiporeceta
        print("1. VALORES DEL ENUM tiporeceta:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                t.typname AS enum_name,
                e.enumlabel AS enum_value,
                e.enumsortorder AS sort_order
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname = 'tiporeceta'
            ORDER BY e.enumsortorder
        """))
        
        enum_values = []
        for row in result:
            print(f"   - {row.enum_value} (orden: {row.sort_order})")
            enum_values.append(row.enum_value)
        
        if not enum_values:
            print("   ⚠️  ADVERTENCIA: No se encontró el enum 'tiporeceta'")
        print()
        
        # 2. Verificar estructura de la tabla
        print("2. ESTRUCTURA DE LA TABLA recetas:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'recetas'
            ORDER BY ordinal_position
        """))
        
        for row in result:
            nullable = "NULL" if row.is_nullable == 'YES' else "NOT NULL"
            print(f"   - {row.column_name}: {row.data_type} ({row.udt_name}) {nullable}")
        print()
        
        # 3. Verificar datos actuales
        print("3. DATOS ACTUALES EN LA TABLA recetas:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                id,
                nombre,
                tipo,
                porciones,
                activa,
                fecha_creacion
            FROM recetas
            ORDER BY fecha_creacion DESC
            LIMIT 10
        """))
        
        recetas = []
        for row in result:
            recetas.append(row)
            tipo_str = str(row.tipo) if row.tipo else 'NULL'
            activa_str = "✓" if row.activa else "✗"
            print(f"   ID {row.id}: {row.nombre} | Tipo: {tipo_str} | Porciones: {row.porciones} | Activa: {activa_str}")
        
        if not recetas:
            print("   ℹ️  No hay recetas en la base de datos")
        print()
        
        # 4. Contar por tipo
        print("4. CONTEO POR TIPO:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                tipo,
                COUNT(*) AS cantidad,
                COUNT(*) FILTER (WHERE activa = true) AS activas,
                COUNT(*) FILTER (WHERE activa = false) AS inactivas
            FROM recetas
            GROUP BY tipo
            ORDER BY tipo
        """))
        
        for row in result:
            tipo_str = str(row.tipo) if row.tipo else 'NULL'
            print(f"   - {tipo_str}: {row.cantidad} total ({row.activas} activas, {row.inactivas} inactivas)")
        print()
        
        # 5. Verificar valores problemáticos
        print("5. VERIFICACIÓN DE VALORES:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                id,
                nombre,
                tipo,
                CASE 
                    WHEN tipo::text NOT IN ('desayuno', 'almuerzo', 'cena') 
                    THEN 'VALOR INVÁLIDO' 
                    ELSE 'OK' 
                END AS estado
            FROM recetas
            WHERE tipo::text NOT IN ('desayuno', 'almuerzo', 'cena')
               OR tipo IS NULL
        """))
        
        problemas = list(result)
        if problemas:
            print("   ⚠️  Se encontraron valores problemáticos:")
            for row in problemas:
                tipo_str = str(row.tipo) if row.tipo else 'NULL'
                print(f"      - ID {row.id}: {row.nombre} | Tipo: {tipo_str} | Estado: {row.estado}")
        else:
            print("   ✓ Todos los valores son válidos")
        print()
        
        # 6. Resumen
        print("6. RESUMEN:")
        print("-" * 80)
        result = session.execute(text("""
            SELECT 
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE activa = true) AS activas,
                COUNT(DISTINCT tipo) AS tipos_unicos
            FROM recetas
        """))
        
        row = result.fetchone()
        print(f"   - Total de recetas: {row.total}")
        print(f"   - Recetas activas: {row.activas}")
        print(f"   - Tipos únicos: {row.tipos_unicos}")
        print()
        
        # 7. Verificar si el enum acepta los valores esperados
        print("7. PRUEBA DE VALORES DEL ENUM:")
        print("-" * 80)
        valores_esperados = ['desayuno', 'almuerzo', 'cena']
        valores_encontrados = [v.lower() for v in enum_values]
        
        for valor in valores_esperados:
            if valor in valores_encontrados:
                print(f"   ✓ '{valor}' está en el enum")
            else:
                print(f"   ✗ '{valor}' NO está en el enum")
        
        print()
        print("=" * 80)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    verificar_recetas()
