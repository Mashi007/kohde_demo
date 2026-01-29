"""
Rutas API para módulo de Chat AI.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.chat.chat_service import chat_service

bp = Blueprint('chat', __name__)

# ========== RUTAS DE CONVERSACIONES ==========

@bp.route('/conversaciones', methods=['GET'])
def listar_conversaciones():
    """Lista conversaciones del usuario."""
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        activa = request.args.get('activa', type=bool)
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))
        
        conversaciones = chat_service.listar_conversaciones(
            db.session,
            usuario_id=usuario_id,
            activa=activa,
            skip=skip,
            limit=limit
        )
        
        return jsonify([c.to_dict() for c in conversaciones]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/conversaciones', methods=['POST'])
def crear_conversacion():
    """Crea una nueva conversación."""
    try:
        datos = request.get_json()
        
        conversacion = chat_service.crear_conversacion(
            db.session,
            titulo=datos.get('titulo'),
            usuario_id=datos.get('usuario_id'),
            contexto_modulo=datos.get('contexto_modulo')
        )
        
        return jsonify(conversacion.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/conversaciones/<int:conversacion_id>', methods=['GET'])
def obtener_conversacion(conversacion_id):
    """Obtiene una conversación con sus mensajes."""
    try:
        conversacion = chat_service.obtener_conversacion(db.session, conversacion_id)
        if not conversacion:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        resultado = conversacion.to_dict()
        resultado['mensajes'] = [m.to_dict() for m in conversacion.mensajes]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/conversaciones/<int:conversacion_id>', methods=['DELETE'])
def eliminar_conversacion(conversacion_id):
    """Elimina (marca como inactiva) una conversación."""
    try:
        eliminada = chat_service.eliminar_conversacion(db.session, conversacion_id)
        if not eliminada:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        return jsonify({'message': 'Conversación eliminada correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== RUTAS DE MENSAJES ==========

@bp.route('/conversaciones/<int:conversacion_id>/mensajes', methods=['POST'])
def enviar_mensaje(conversacion_id):
    """Envía un mensaje y obtiene respuesta del AI."""
    try:
        datos = request.get_json()
        contenido = datos.get('contenido', '').strip()
        
        if not contenido:
            return jsonify({'error': 'El contenido del mensaje no puede estar vacío'}), 400
        
        usuario_id = datos.get('usuario_id')
        
        resultado = chat_service.enviar_mensaje(
            db.session,
            conversacion_id,
            contenido,
            usuario_id=usuario_id
        )
        
        return jsonify(resultado), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/conversaciones/<int:conversacion_id>/mensajes', methods=['GET'])
def listar_mensajes(conversacion_id):
    """Lista los mensajes de una conversación."""
    try:
        conversacion = chat_service.obtener_conversacion(db.session, conversacion_id)
        if not conversacion:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        mensajes = [m.to_dict() for m in conversacion.mensajes]
        return jsonify(mensajes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
