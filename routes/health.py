"""
Ruta de salud para verificar el estado del servidor.
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text
from utils.route_helpers import success_response, error_response
from utils.db_helpers import verify_db_connection, verify_foreign_keys

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Verifica el estado del servidor y la conexión a la base de datos."""
    try:
        db_info = verify_db_connection()
        
        response_data = {
            'status': 'ok' if db_info['connected'] else 'error',
            'database': db_info['status'],
            'message': db_info['message'],
            'timestamp': db.session.execute(text('SELECT NOW()')).scalar().isoformat()
        }
        
        if db_info['connected']:
            return success_response(response_data)
        else:
            return error_response(db_info['message'], 503, 'DATABASE_ERROR')
    except Exception as e:
        return error_response(f'Error al verificar salud: {str(e)}', 500, 'INTERNAL_ERROR')

@bp.route('/api/health', methods=['GET'])
def api_health_check():
    """Verifica el estado del API con información detallada."""
    try:
        db_info = verify_db_connection()
        
        response_data = {
            'status': 'ok' if db_info['connected'] else 'error',
            'database': db_info['status'],
            'message': db_info['message'],
            'api': 'running',
            'timestamp': db.session.execute(text('SELECT NOW()')).scalar().isoformat()
        }
        
        # Agregar información de foreign keys si la conexión es exitosa
        if db_info['connected']:
            try:
                fk_info = verify_foreign_keys()
                response_data['foreign_keys'] = {
                    'count': fk_info.get('foreign_keys_count', 0),
                    'status': fk_info.get('status', 'unknown')
                }
            except Exception:
                pass  # No crítico
        
        if db_info['connected']:
            return success_response(response_data)
        else:
            return error_response(db_info['message'], 503, 'DATABASE_ERROR')
    except Exception as e:
        return error_response(f'Error al verificar salud: {str(e)}', 500, 'INTERNAL_ERROR')

@bp.route('/health/db', methods=['GET'])
def db_health_check():
    """Verificación detallada de la base de datos."""
    try:
        db_info = verify_db_connection()
        fk_info = verify_foreign_keys()
        
        response_data = {
            'connection': db_info,
            'foreign_keys': fk_info
        }
        
        return success_response(response_data)
    except Exception as e:
        return error_response(f'Error al verificar BD: {str(e)}', 500, 'INTERNAL_ERROR')
