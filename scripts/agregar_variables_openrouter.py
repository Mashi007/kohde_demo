"""
Script para agregar variables de OpenRouter al archivo .env
"""
import os
from pathlib import Path

# ⚠️ IMPORTANTE: NO hardcodees tokens aquí. Este script ahora solicita el token al usuario.
# Variables de OpenRouter (valores por defecto, el token se solicitará)
VARIABLES_OPENROUTER_DEFAULTS = {
    'OPENAI_BASE_URL': 'https://openrouter.ai/api/v1',
    'OPENAI_MODEL': 'openai/gpt-3.5-turbo',
    'OPENROUTER_HTTP_REFERER': 'https://github.com/Mashi007/kohde_demo.git',
    'OPENROUTER_X_TITLE': 'Kohde ERP Restaurantes'
}

def agregar_variables_al_env():
    """Agrega las variables de OpenRouter al archivo .env"""
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / '.env'
    
    print("=" * 60)
    print("AGREGAR VARIABLES DE OPENROUTER AL .env")
    print("=" * 60)
    
    # Leer contenido actual del .env si existe
    contenido_actual = ""
    variables_existentes = set()
    
    if env_file.exists():
        print(f"\n📄 Archivo .env encontrado: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            contenido_actual = f.read()
            # Extraer nombres de variables existentes
            for linea in contenido_actual.split('\n'):
                linea = linea.strip()
                if linea and not linea.startswith('#') and '=' in linea:
                    var_name = linea.split('=')[0].strip()
                    variables_existentes.add(var_name)
        print(f"   Variables existentes encontradas: {len(variables_existentes)}")
    else:
        print(f"\n📄 Creando nuevo archivo .env: {env_file}")
    
    # Solicitar token si no está en variables de entorno
    openrouter_token = os.getenv('OPENROUTER_API_KEY', '').strip()
    
    if not openrouter_token:
        print("\n⚠️  No se encontró OPENROUTER_API_KEY en variables de entorno.")
        print("\nPor favor, proporciona tu token de OpenRouter:")
        print("1. Ve a https://openrouter.ai/keys")
        print("2. Crea un nuevo token")
        print("3. Ingresa el token aquí (o configura OPENROUTER_API_KEY en tu entorno)")
        print("\nO ejecuta este script con:")
        print("   OPENROUTER_API_KEY=tu-token-aqui python scripts/agregar_variables_openrouter.py")
        return
    
    # Verificar qué variables ya existen
    variables_openrouter = {
        'OPENROUTER_API_KEY': openrouter_token,
        **VARIABLES_OPENROUTER_DEFAULTS
    }
    
    variables_a_agregar = []
    variables_a_actualizar = []
    
    for var_name, var_value in variables_openrouter.items():
        if var_name in variables_existentes:
            variables_a_actualizar.append(var_name)
        else:
            variables_a_agregar.append(var_name)
    
    if variables_a_agregar or variables_a_actualizar:
        print(f"\n📝 Variables a agregar: {', '.join(variables_a_agregar) if variables_a_agregar else 'Ninguna'}")
        print(f"🔄 Variables a actualizar: {', '.join(variables_a_actualizar) if variables_a_actualizar else 'Ninguna'}")
        
        # Procesar líneas del .env
        lineas_nuevas = []
        variables_procesadas = set()
        
        for linea in contenido_actual.split('\n'):
            linea_original = linea
            linea_stripped = linea.strip()
            
            # Si es una variable de OpenRouter, reemplazarla
            if linea_stripped and not linea_stripped.startswith('#') and '=' in linea_stripped:
                var_name = linea_stripped.split('=')[0].strip()
                if var_name in variables_openrouter:
                    # Reemplazar con el nuevo valor
                    nueva_linea = f"{var_name}={variables_openrouter[var_name]}"
                    lineas_nuevas.append(nueva_linea)
                    variables_procesadas.add(var_name)
                    continue
            
            lineas_nuevas.append(linea_original)
        
        # Agregar variables que no existían
        if not contenido_actual.strip().endswith('\n') and contenido_actual:
            lineas_nuevas.append('')
        
        # Agregar sección de OpenRouter si hay variables nuevas
        if variables_a_agregar:
            lineas_nuevas.append("\n# ========== CONFIGURACIÓN OPENROUTER AI ==========")
            for var_name in variables_a_agregar:
                if var_name not in variables_procesadas:
                    lineas_nuevas.append(f"{var_name}={variables_openrouter[var_name]}")
        
        # Escribir el archivo actualizado
        nuevo_contenido = '\n'.join(lineas_nuevas)
        
        # Crear backup del .env original
        if env_file.exists():
            backup_file = base_dir / '.env.backup'
            with open(env_file, 'r', encoding='utf-8') as f:
                with open(backup_file, 'w', encoding='utf-8') as bf:
                    bf.write(f.read())
            print(f"\n💾 Backup creado: {backup_file}")
        
        # Escribir el nuevo contenido
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
        
        print(f"\n✅ Variables agregadas/actualizadas en: {env_file}")
        print("\n📋 Variables configuradas:")
        for var_name in variables_openrouter.keys():
            estado = "✅ Actualizada" if var_name in variables_existentes else "➕ Agregada"
            print(f"   {estado}: {var_name}")
        
    else:
        print("\n✅ Todas las variables de OpenRouter ya están configuradas")
    
    print("\n" + "=" * 60)
    print("📝 IMPORTANTE:")
    print("=" * 60)
    print("1. Reinicia el servidor Flask para que las variables surtan efecto")
    print("2. Las variables ahora son permanentes (no se pierden al reiniciar)")
    print("3. Si necesitas cambiar el modelo, edita OPENAI_MODEL en el .env")
    print("4. Ver modelos disponibles en: https://openrouter.ai/models")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    agregar_variables_al_env()
