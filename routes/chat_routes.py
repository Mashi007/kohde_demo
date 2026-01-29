"""
Rutas API para módulo de Chat AI.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.chat.chat_service import chat_service
from utils.route_helpers import (
    handle_db_transaction, require_field,
    validate_positive_int, success_response,
    error_response, paginated_response
)

bp = Blueprint('chat', __name__)

# ========== RUTAS DE CONVERSACIONES ==========

@bp.route('/conversaciones', methods=['GET'])
def listar_conversaciones():
    """Lista conversaciones del usuario."""
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        activa = request.args.get('activa', type=bool)
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 50), 'limit')
        
        if usuario_id:
            validate_positive_int(usuario_id, 'usuario_id')
        
        conversaciones = chat_service.listar_conversaciones(
            db.session,
            usuario_id=usuario_id,
            activa=activa,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([c.to_dict() for c in conversaciones], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/conversaciones', methods=['POST'])
@handle_db_transaction
def crear_conversacion():
    """Crea una nueva conversación."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    conversacion = chat_service.crear_conversacion(
        db.session,
        titulo=datos.get('titulo'),
        usuario_id=datos.get('usuario_id'),
        contexto_modulo=datos.get('contexto_modulo')
    )
    db.session.commit()
    
    return success_response(conversacion.to_dict(), 201, 'Conversación creada correctamente')

@bp.route('/conversaciones/<int:conversacion_id>', methods=['GET'])
def obtener_conversacion(conversacion_id):
    """Obtiene una conversación con sus mensajes."""
    try:
        validate_positive_int(conversacion_id, 'conversacion_id')
        conversacion = chat_service.obtener_conversacion(db.session, conversacion_id)
        if not conversacion:
            return error_response('Conversación no encontrada', 404, 'NOT_FOUND')
        
        resultado = conversacion.to_dict()
        resultado['mensajes'] = [m.to_dict() for m in conversacion.mensajes]
        
        return success_response(resultado)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/conversaciones/<int:conversacion_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_conversacion(conversacion_id):
    """Elimina (marca como inactiva) una conversación."""
    validate_positive_int(conversacion_id, 'conversacion_id')
    eliminada = chat_service.eliminar_conversacion(db.session, conversacion_id)
    if not eliminada:
        return error_response('Conversación no encontrada', 404, 'NOT_FOUND')
    
    db.session.commit()
    return success_response(None, message='Conversación eliminada correctamente')

# ========== RUTAS DE MENSAJES ==========

@bp.route('/conversaciones/<int:conversacion_id>/mensajes', methods=['POST'])
@handle_db_transaction
def enviar_mensaje(conversacion_id):
    """Envía un mensaje y obtiene respuesta del AI."""
    validate_positive_int(conversacion_id, 'conversacion_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    contenido = datos.get('contenido', '').strip()
    if not contenido:
        return error_response('El contenido del mensaje no puede estar vacío', 400, 'VALIDATION_ERROR')
    
    usuario_id = datos.get('usuario_id')
    
    resultado = chat_service.enviar_mensaje(
        db.session,
        conversacion_id,
        contenido,
        usuario_id=usuario_id
    )
    db.session.commit()
    
    return success_response(resultado)

@bp.route('/conversaciones/<int:conversacion_id>/mensajes', methods=['GET'])
def listar_mensajes(conversacion_id):
    """Lista los mensajes de una conversación."""
    try:
        validate_positive_int(conversacion_id, 'conversacion_id')
        conversacion = chat_service.obtener_conversacion(db.session, conversacion_id)
        if not conversacion:
            return error_response('Conversación no encontrada', 404, 'NOT_FOUND')
        
        mensajes = [m.to_dict() for m in conversacion.mensajes]
        return success_response(mensajes)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')
