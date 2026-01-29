"""
Ruta de salud para verificar el estado del servidor.
"""
from flask import Blueprint, jsonify
from models import db
from sqlalchemy import text

bp = Blueprint('health', __name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """Verifica el estado del servidor y la conexión a la base de datos."""
    try:
        # Verificar conexión a BD
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'database': db_status,
        'message': 'Server is running'
    }), 200

@bp.route('/api/health', methods=['GET'])
def api_health_check():
    """Verifica el estado del API."""
    try:
        # Verificar conexión a BD
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'database': db_status,
        'message': 'API is running'
    }), 200
