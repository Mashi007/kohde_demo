"""
Configuración del sistema ERP para cadena de restaurantes.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent

class Config:
    """Configuración base."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Base de datos PostgreSQL
    # Render proporciona DATABASE_URL automáticamente cuando conectas PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL:
        # Si existe DATABASE_URL (Render), usarla directamente
        # Render puede usar postgres:// pero SQLAlchemy necesita postgresql://
        # Usar psycopg3 (psycopg) en lugar de psycopg2 para Python 3.13
        if DATABASE_URL.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql+psycopg://', 1)
        elif DATABASE_URL.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Configuración manual para desarrollo local
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'erp_restaurantes')
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
        SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # Google Cloud Vision API (OCR)
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', '')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Ruta al archivo JSON de credenciales de Google Cloud
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', '')
    
    # Credenciales JSON como string (más fácil para Render manual)
    GOOGLE_APPLICATION_CREDENTIALS_JSON = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON', '')
    
    # Workload Identity Federation (Render automático)
    WORKLOAD_IDENTITY_PROVIDER = os.getenv('WORKLOAD_IDENTITY_PROVIDER', '')
    SERVICE_ACCOUNT_EMAIL = os.getenv('SERVICE_ACCOUNT_EMAIL', '')
    RENDER_SERVICE_ID = os.getenv('RENDER_SERVICE_ID', '')
    
    # WhatsApp Business API
    WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
    WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'whatsapp-verify-token')
    
    # SendGrid (Email)
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@restaurantes.com')
    
    # Almacenamiento de imágenes
    UPLOAD_FOLDER = BASE_DIR / 'uploads' / 'facturas'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    
    # Configuración de inventario
    STOCK_MINIMUM_THRESHOLD_PERCENTAGE = float(os.getenv('STOCK_MINIMUM_THRESHOLD_PERCENTAGE', '0.2'))  # 20% buffer
    
    # Configuración de facturas
    IVA_PERCENTAGE = float(os.getenv('IVA_PERCENTAGE', '0.15'))  # 15% IVA por defecto

# Crear directorio de uploads si no existe
Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
