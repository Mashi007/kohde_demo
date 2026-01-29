"""
Aplicación principal del ERP para cadena de restaurantes.
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from models import db

# Importar rutas
from routes import (
    crm_routes,
    contabilidad_routes,
    logistica_routes,
    compras_routes,
    planificacion_routes,
    configuracion_routes
)
from routes import whatsapp_webhook
from routes import health

def create_app():
    """Factory function para crear la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Habilitar CORS
    # Permitir requests desde el frontend
    CORS(app, origins=[
        "https://kfronend-demo.onrender.com",
        "http://localhost:3000",  # Para desarrollo local
        "http://localhost:5173",  # Vite dev server alternativo
    ])
    
    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Registrar blueprints
    app.register_blueprint(health.bp)  # Health check sin prefijo
    app.register_blueprint(crm_routes.bp, url_prefix='/api/crm')
    app.register_blueprint(contabilidad_routes.bp, url_prefix='/api/contabilidad')
    app.register_blueprint(logistica_routes.bp, url_prefix='/api/logistica')
    app.register_blueprint(compras_routes.bp, url_prefix='/api/compras')
    app.register_blueprint(planificacion_routes.bp, url_prefix='/api/planificacion')
    app.register_blueprint(configuracion_routes.bp, url_prefix='/api/configuracion')
    app.register_blueprint(whatsapp_webhook.bp, url_prefix='/whatsapp')
    
    # Crear tablas en la base de datos
    with app.app_context():
        try:
            db.create_all()
            print("✅ Tablas de base de datos creadas correctamente")
        except Exception as e:
            print(f"⚠️ Error al crear tablas: {e}")
            import traceback
            traceback.print_exc()
    
    return app

# Crear instancia de la aplicación para Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
