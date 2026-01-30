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
        'https://kohde-demo-1.onrender.com,https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173'
    ).split(',')
    
    CORS(app, 
         origins=[origin.strip() for origin in cors_origins],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         expose_headers=['X-Total-Count', 'X-Page-Size', 'X-Page-Offset']
    )
    
    # Manejar solicitudes OPTIONS (preflight) explícitamente
    @app.before_request
    def handle_preflight():
        """Maneja solicitudes OPTIONS (preflight) para CORS."""
        from flask import request, jsonify
        if request.method == 'OPTIONS':
            response = jsonify({})
            origin = request.headers.get('Origin')
            if origin and origin in [origin.strip() for origin in cors_origins]:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
                response.headers['Access-Control-Max-Age'] = '3600'
            return response
    
    # Agregar headers CORS a todas las respuestas
    @app.after_request
    def after_request(response):
        """Agrega headers CORS y de seguridad a todas las respuestas."""
        try:
            from flask import request
            origin = request.headers.get('Origin')
            if origin and origin in [origin.strip() for origin in cors_origins]:
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept'
        except Exception as e:
            # Si hay algún error obteniendo el origin, continuar sin él
            import logging
            logging.warning(f"Error obteniendo Origin header: {str(e)}")
        
        # Headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Aplicar configuración del pool de conexiones después de init_app
    # Flask-SQLAlchemy crea el engine en init_app, así que lo reconfiguramos aquí
    if hasattr(Config, 'SQLALCHEMY_ENGINE_OPTIONS'):
        from sqlalchemy import create_engine
        # Obtener la URI actual
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Crear nuevo engine con las opciones del pool
        new_engine = create_engine(database_uri, **Config.SQLALCHEMY_ENGINE_OPTIONS)
        # Reemplazar el engine de Flask-SQLAlchemy
        db.engine = new_engine
        # Actualizar el método get_engine para que devuelva nuestro engine
        db.get_engine = lambda bind=None: new_engine
    
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
    # IMPORTANTE: En producción, usar migraciones (Alembic) en lugar de create_all()
    # Solo crear tablas automáticamente en desarrollo (DEBUG=True)
    import os
    is_production = os.getenv('ENVIRONMENT', '').lower() == 'production' or not Config.DEBUG
    
    if not is_production:
        # Solo en desarrollo: crear tablas automáticamente
        with app.app_context():
            try:
                db.create_all()
                import logging
                logger = logging.getLogger(__name__)
                logger.info("✅ Tablas de base de datos verificadas/creadas correctamente (modo desarrollo)")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"⚠️ Error al crear tablas: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
    else:
        # En producción: solo verificar conexión, no crear tablas
        with app.app_context():
            try:
                # Solo verificar que la conexión funciona
                db.session.execute(db.text('SELECT 1'))
                import logging
                logger = logging.getLogger(__name__)
                logger.info("✅ Conexión a base de datos verificada (modo producción - usar migraciones Alembic)")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"⚠️ Error al conectar a base de datos: {e}", exc_info=True)
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
