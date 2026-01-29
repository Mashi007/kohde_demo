"""
Aplicación principal del ERP para cadena de restaurantes.
"""
from flask import Flask, request
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
    configuracion_routes,
    reportes_routes,
    chat_routes
)
from routes import whatsapp_webhook
from routes import health

def create_app():
    """Factory function para crear la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurar logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Habilitar CORS
    # Permitir requests desde el frontend
    import os
    cors_origins = os.getenv('CORS_ORIGINS', 
        'https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173'
    ).split(',')
    
    CORS(app, 
         origins=[origin.strip() for origin in cors_origins],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         expose_headers=['X-Total-Count', 'X-Page-Size', 'X-Page-Offset']
    )
    
    # Agregar headers CORS a todas las respuestas
    @app.after_request
    def after_request(response):
        """Agrega headers CORS y de seguridad a todas las respuestas."""
        origin = request.headers.get('Origin')
        if origin and origin in [origin.strip() for origin in cors_origins]:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
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
    app.register_blueprint(reportes_routes.bp, url_prefix='/api/reportes')
    app.register_blueprint(chat_routes.bp, url_prefix='/api/chat')
    app.register_blueprint(whatsapp_webhook.bp, url_prefix='/whatsapp')
    
    # Crear tablas en la base de datos
    # Nota: En producción, usar migraciones (Alembic) en lugar de create_all()
    with app.app_context():
        try:
            # Solo crear tablas si no existen (útil para desarrollo)
            # En producción, usar migraciones SQL o Alembic
            db.create_all()
            import logging
            logger = logging.getLogger(__name__)
            logger.info("✅ Tablas de base de datos verificadas/creadas correctamente")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"⚠️ Error al crear tablas: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
    
    # Configurar tareas programadas (solo en producción o cuando se especifique)
    import os
    if os.getenv('ENABLE_SCHEDULER', 'true').lower() == 'true':
        try:
            from modules.logistica.tareas_programadas import configurar_tareas_programadas
            configurar_tareas_programadas(app)
            print("✅ Tareas programadas configuradas: Recálculo de costos cada sábado a las 2:00 AM")
        except Exception as e:
            print(f"⚠️ Advertencia: No se pudo inicializar el scheduler: {e}")
            import traceback
            traceback.print_exc()
    
    return app

# Crear instancia de la aplicación para Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
