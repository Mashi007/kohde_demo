"""
Script para verificar que el chat AI puede acceder a la base de datos
y que tiene estructura optimizada para consultas rápidas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from models import db
from sqlalchemy import text, inspect

def verificar_indices():
    """Verifica que existan índices en las tablas principales."""
    print("=" * 70)
    print("VERIFICACIÓN DE ÍNDICES EN BASE DE DATOS")
    print("=" * 70)
    print()
    
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Tablas principales que deberían tener índices
        tablas_importantes = [
            'items',
            'inventario',
            'proveedores',
            'facturas',
            'recetas',
            'programacion_menu',
            'charolas',
            'mermas'
        ]
        
        print("📊 ÍNDICES ENCONTRADOS POR TABLA:")
        print("-" * 70)
        
        total_indices = 0
        for tabla in tablas_importantes:
            try:
                indices = inspector.get_indexes(tabla)
                if indices:
                    print(f"\n✅ {tabla}: {len(indices)} índice(s)")
                    for idx in indices[:5]:  # Mostrar primeros 5
                        columnas = ', '.join(idx['column_names'])
                        unico = " (único)" if idx.get('unique') else ""
                        print(f"   - {idx['name']}: {columnas}{unico}")
                    if len(indices) > 5:
                        print(f"   ... y {len(indices) - 5} más")
                    total_indices += len(indices)
                else:
                    print(f"⚠️  {tabla}: Sin índices")
            except Exception as e:
                print(f"❌ {tabla}: Error al verificar - {str(e)}")
        
        print()
        print(f"📈 Total de índices encontrados: {total_indices}")
        print()
        
        return total_indices > 0

def verificar_estructura_tablas():
    """Verifica la estructura de las tablas principales."""
    print("=" * 70)
    print("VERIFICACIÓN DE ESTRUCTURA DE TABLAS")
    print("=" * 70)
    print()
    
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        tablas_principales = {
            'items': ['id', 'codigo', 'nombre', 'activo', 'proveedor_autorizado_id'],
            'inventario': ['id', 'item_id', 'cantidad_actual', 'cantidad_minima', 'ubicacion'],
            'proveedores': ['id', 'nombre', 'ruc', 'activo'],
            'facturas': ['id', 'numero_factura', 'proveedor_id', 'estado', 'fecha_recepcion'],
            'recetas': ['id', 'nombre', 'tipo', 'activa'],
            'programacion_menu': ['id', 'fecha', 'ubicacion', 'tiempo_comida', 'activa'],
        }
        
        print("📋 ESTRUCTURA DE TABLAS PRINCIPALES:")
        print("-" * 70)
        
        for tabla, columnas_esperadas in tablas_principales.items():
            try:
                columnas = inspector.get_columns(tabla)
                nombres_columnas = [col['name'] for col in columnas]
                
                print(f"\n✅ {tabla}:")
                print(f"   Columnas encontradas: {len(nombres_columnas)}")
                
                # Verificar columnas importantes
                columnas_encontradas = []
                for col_esperada in columnas_esperadas:
                    if col_esperada in nombres_columnas:
                        columnas_encontradas.append(col_esperada)
                    else:
                        print(f"   ⚠️  Columna faltante: {col_esperada}")
                
                if len(columnas_encontradas) == len(columnas_esperadas):
                    print(f"   ✅ Todas las columnas esperadas presentes")
            except Exception as e:
                print(f"❌ {tabla}: Error - {str(e)}")
        
        print()

def verificar_capacidad_consulta():
    """Verifica que se puedan ejecutar consultas SELECT."""
    print("=" * 70)
    print("VERIFICACIÓN DE CAPACIDAD DE CONSULTAS")
    print("=" * 70)
    print()
    
    app = create_app()
    with app.app_context():
        consultas_prueba = [
            {
                'nombre': 'Contar items activos',
                'sql': 'SELECT COUNT(*) as total FROM items WHERE activo = true'
            },
            {
                'nombre': 'Items con inventario bajo',
                'sql': '''
                    SELECT i.nombre, inv.cantidad_actual, inv.cantidad_minima 
                    FROM inventario inv 
                    JOIN items i ON inv.item_id = i.id 
                    WHERE inv.cantidad_actual < inv.cantidad_minima AND i.activo = true 
                    LIMIT 5
                '''
            },
            {
                'nombre': 'Proveedores activos',
                'sql': 'SELECT COUNT(*) as total FROM proveedores WHERE activo = true'
            }
        ]
        
        print("🧪 EJECUTANDO CONSULTAS DE PRUEBA:")
        print("-" * 70)
        
        todas_exitosas = True
        for consulta in consultas_prueba:
            try:
                resultado = db.session.execute(text(consultas_prueba[0]['sql']))
                filas = resultado.fetchall()
                
                print(f"✅ {consulta['nombre']}: Ejecutada correctamente")
                if filas:
                    print(f"   Resultado: {filas[0]}")
            except Exception as e:
                print(f"❌ {consulta['nombre']}: Error - {str(e)}")
                todas_exitosas = False
        
        print()
        return todas_exitosas

def verificar_prompt_sistema():
    """Verifica que el prompt del sistema incluya información de la BD."""
    print("=" * 70)
    print("VERIFICACIÓN DEL PROMPT DEL SISTEMA")
    print("=" * 70)
    print()
    
    from modules.chat.chat_service import chat_service
    
    prompt = chat_service._construir_prompt_sistema()
    
    elementos_clave = [
        ('TABLAS DISPONIBLES', 'Información de tablas'),
        ('QUERY_DB', 'Formato para consultas'),
        ('items', 'Tabla items'),
        ('inventario', 'Tabla inventario'),
        ('proveedores', 'Tabla proveedores'),
        ('facturas', 'Tabla facturas'),
        ('recetas', 'Tabla recetas'),
        ('índices', 'Información de índices'),
        ('LIMIT', 'Uso de LIMIT'),
        ('SELECT', 'Consultas SELECT')
    ]
    
    print("📝 ELEMENTOS EN EL PROMPT:")
    print("-" * 70)
    
    todos_presentes = True
    for elemento, descripcion in elementos_clave:
        if elemento in prompt:
            print(f"✅ {descripcion}: Presente")
        else:
            print(f"❌ {descripcion}: FALTANTE")
            todos_presentes = False
    
    print()
    print(f"📏 Longitud del prompt: {len(prompt)} caracteres")
    print()
    
    return todos_presentes

def verificar_metodo_ejecucion():
    """Verifica que el método de ejecución de consultas funcione."""
    print("=" * 70)
    print("VERIFICACIÓN DEL MÉTODO DE EJECUCIÓN")
    print("=" * 70)
    print()
    
    from modules.chat.chat_service import chat_service
    
    # Verificar que el método existe
    metodos_requeridos = [
        '_ejecutar_consulta_db',
        '_llamar_openai_con_db',
        '_construir_prompt_sistema'
    ]
    
    print("🔧 MÉTODOS DEL SERVICIO:")
    print("-" * 70)
    
    todos_presentes = True
    for metodo in metodos_requeridos:
        if hasattr(chat_service, metodo):
            print(f"✅ {metodo}: Existe")
        else:
            print(f"❌ {metodo}: NO existe")
            todos_presentes = False
    
    print()
    
    # Verificar que _ejecutar_consulta_db valide correctamente
    if hasattr(chat_service, '_ejecutar_consulta_db'):
        print("🔒 VALIDACIÓN DE SEGURIDAD:")
        print("-" * 70)
        
        app = create_app()
        with app.app_context():
            # Probar consulta válida
            resultado_valido = chat_service._ejecutar_consulta_db(
                db.session,
                "SELECT COUNT(*) FROM items WHERE activo = true LIMIT 1"
            )
            if resultado_valido.get('error') is None:
                print("✅ Consulta SELECT válida: Aceptada")
            else:
                print(f"❌ Consulta SELECT válida: Rechazada - {resultado_valido.get('error')}")
            
            # Probar consulta peligrosa (debe ser rechazada)
            resultado_peligroso = chat_service._ejecutar_consulta_db(
                db.session,
                "DELETE FROM items WHERE id = 1"
            )
            if resultado_peligroso.get('error'):
                print("✅ Consulta DELETE peligrosa: Rechazada correctamente")
            else:
                print("❌ Consulta DELETE peligrosa: NO fue rechazada (riesgo de seguridad)")
    
    print()
    return todos_presentes

def main():
    """Ejecuta todas las verificaciones."""
    print()
    print("🔍 VERIFICACIÓN COMPLETA: ACCESO A BASE DE DATOS DEL CHAT AI")
    print()
    
    resultados = []
    
    resultados.append(("Índices en BD", verificar_indices()))
    resultados.append(("Estructura de tablas", verificar_estructura_tablas()))
    resultados.append(("Capacidad de consultas", verificar_capacidad_consulta()))
    resultados.append(("Prompt del sistema", verificar_prompt_sistema()))
    resultados.append(("Método de ejecución", verificar_metodo_ejecucion()))
    
    print()
    print("=" * 70)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 70)
    print()
    
    for nombre, resultado in resultados:
        estado = "✅ OK" if resultado else "❌ FALLO"
        print(f"{estado} - {nombre}")
    
    print()
    print("=" * 70)
    
    todos_ok = all(r[1] for r in resultados)
    if todos_ok:
        print("✅ VERIFICACIÓN COMPLETA: El chat AI tiene acceso completo a la BD")
        print("   y estructura optimizada para consultas rápidas")
    else:
        print("⚠️  VERIFICACIÓN: Hay algunos aspectos que necesitan atención")
    
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
