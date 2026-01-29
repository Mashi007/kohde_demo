"""
Rutas API para módulo de Configuración.
Incluye: WhatsApp y AI (OpenAI)
"""
from flask import Blueprint, request, jsonify
from modules.configuracion.whatsapp import whatsapp_config_service
from modules.configuracion.ai import ai_config_service
from modules.configuracion.notificaciones import notificaciones_config_service

bp = Blueprint('configuracion', __name__)

# ========== RUTAS DE WHATSAPP ==========

@bp.route('/whatsapp', methods=['GET'])
def obtener_configuracion_whatsapp():
    """Obtiene la configuración actual de WhatsApp."""
    try:
        config = whatsapp_config_service.obtener_configuracion()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/verificar', methods=['GET'])
def verificar_whatsapp():
    """Verifica la configuración de WhatsApp."""
    try:
        resultado = whatsapp_config_service.verificar_configuracion()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/probar', methods=['POST'])
def probar_whatsapp():
    """Envía un mensaje de prueba de WhatsApp."""
    try:
        datos = request.get_json()
        numero = datos.get('numero', '').strip()
        mensaje = datos.get('mensaje', 'Mensaje de prueba desde ERP')
        
        if not numero:
            return jsonify({'error': 'Número de teléfono requerido'}), 400
        
        resultado = whatsapp_config_service.enviar_mensaje_prueba(numero, mensaje)
        
        if resultado.get('exito'):
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== RUTAS DE AI (OPENAI) ==========

@bp.route('/ai', methods=['GET'])
def obtener_configuracion_ai():
    """Obtiene la configuración actual de AI."""
    try:
        config = ai_config_service.obtener_configuracion()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/verificar', methods=['GET'])
def verificar_ai():
    """Verifica la configuración de AI."""
    try:
        resultado = ai_config_service.verificar_configuracion()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ai/probar', methods=['POST'])
def probar_ai():
    """Envía un mensaje de prueba al AI."""
    try:
        datos = request.get_json()
        mensaje = datos.get('mensaje', 'Hola, ¿puedes responder con OK?')
        
        resultado = ai_config_service.enviar_mensaje_prueba(mensaje)
        
        if resultado.get('exito'):
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== RUTA GENERAL ==========

# ========== RUTAS DE NOTIFICACIONES POR EMAIL ==========

@bp.route('/notificaciones', methods=['GET'])
def obtener_configuracion_notificaciones():
    """Obtiene la configuración actual de notificaciones por email."""
    try:
        config = notificaciones_config_service.obtener_configuracion()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/notificaciones', methods=['PUT'])
def actualizar_email_notificaciones():
    """Actualiza el email de notificaciones de pedidos."""
    try:
        datos = request.get_json()
        email = datos.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        resultado = notificaciones_config_service.actualizar_email_notificaciones(email)
        
        if resultado.get('exito'):
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/notificaciones/verificar', methods=['GET'])
def verificar_notificaciones():
    """Verifica la configuración de notificaciones por email."""
    try:
        resultado = notificaciones_config_service.verificar_configuracion()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/notificaciones/probar', methods=['POST'])
def probar_notificaciones():
    """Envía un email de prueba."""
    try:
        datos = request.get_json()
        email_destino = datos.get('email', '').strip() if datos else None
        
        resultado = notificaciones_config_service.enviar_email_prueba(email_destino)
        
        if resultado.get('exito'):
            return jsonify(resultado), 200
        else:
            return jsonify(resultado), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== RUTA GENERAL ==========

@bp.route('/estado', methods=['GET'])
def obtener_estado_general():
    """Obtiene el estado de todas las configuraciones."""
    try:
        whatsapp_config = whatsapp_config_service.obtener_configuracion()
        ai_config = ai_config_service.obtener_configuracion()
        notificaciones_config = notificaciones_config_service.obtener_configuracion()
        
        return jsonify({
            'whatsapp': {
                'configurado': whatsapp_config['estado'] == 'configurado',
                'estado': whatsapp_config['estado']
            },
            'ai': {
                'configurado': ai_config['estado'] == 'configurado',
                'estado': ai_config['estado']
            },
            'notificaciones': {
                'configurado': notificaciones_config['estado'] == 'configurado',
                'estado': notificaciones_config['estado'],
                'email': notificaciones_config['email_notificaciones_pedidos']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
