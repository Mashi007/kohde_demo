"""
Script para verificar la configuración de la base de datos.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno explícitamente
from dotenv import load_dotenv

# Obtener la ruta del directorio raíz
root_dir = Path(__file__).parent.parent
env_path = root_dir / '.env'

print("=" * 60)
print("VERIFICACIÓN DE CONFIGURACIÓN DE BASE DE DATOS")
print("=" * 60)

print(f"\n📁 Directorio raíz: {root_dir}")
print(f"📄 Ruta del .env: {env_path}")
print(f"✅ Archivo .env existe: {env_path.exists()}")

# Cargar .env
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Archivo .env cargado")
else:
    print("❌ Archivo .env NO encontrado")
    # Intentar cargar desde el directorio actual
    load_dotenv()

# Verificar variables de entorno
print("\n🔍 Variables de entorno detectadas:")
print("-" * 60)

database_url = os.getenv('DATABASE_URL')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if database_url:
    # Ocultar contraseña en la salida
    safe_url = database_url
    if '@' in safe_url:
        parts = safe_url.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split(':')
            if len(user_pass) >= 3:
                safe_url = f"{user_pass[0]}:{'*' * 10}@{parts[1]}"
    print(f"✅ DATABASE_URL: {safe_url}")
else:
    print("❌ DATABASE_URL: No configurado")

if db_host:
    print(f"✅ DB_HOST: {db_host}")
else:
    print("⚠️  DB_HOST: No configurado (usará 'localhost' por defecto)")

if db_port:
    print(f"✅ DB_PORT: {db_port}")
else:
    print("⚠️  DB_PORT: No configurado (usará '5432' por defecto)")

if db_name:
    print(f"✅ DB_NAME: {db_name}")
else:
    print("⚠️  DB_NAME: No configurado (usará 'erp_restaurantes' por defecto)")

if db_user:
    print(f"✅ DB_USER: {db_user}")
else:
    print("⚠️  DB_USER: No configurado (usará 'postgres' por defecto)")

if db_password:
    print(f"✅ DB_PASSWORD: {'*' * len(db_password)}")
else:
    print("⚠️  DB_PASSWORD: No configurado (usará 'postgres' por defecto)")

# Verificar configuración final
print("\n🔧 Configuración que se usará:")
print("-" * 60)

from config import Config

if Config.DATABASE_URL:
    safe_uri = Config.SQLALCHEMY_DATABASE_URI
    if '@' in safe_uri:
        parts = safe_uri.split('@')
        if ':' in parts[0]:
            user_pass = parts[0].split(':')
            if len(user_pass) >= 3:
                safe_uri = f"{user_pass[0]}:{'*' * 10}@{parts[1]}"
    print(f"✅ SQLALCHEMY_DATABASE_URI: {safe_uri}")
else:
    print(f"⚠️  SQLALCHEMY_DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")

print("\n" + "=" * 60)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 60)
