"""
Rutas API para configuración del sistema.
"""
from flask import Blueprint, request, jsonify
from modules.configuracion.whatsapp import WhatsAppConfigService

bp = Blueprint('configuracion', __name__)

# ========== RUTAS DE CONFIGURACIÓN WHATSAPP ==========

@bp.route('/whatsapp/verificar', methods=['GET'])
def verificar_whatsapp():
    """Verifica la configuración de WhatsApp."""
    try:
        config = WhatsAppConfigService.verificar_configuracion()
        return jsonify(config), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/probar', methods=['POST'])
def probar_whatsapp():
    """Prueba la conexión con WhatsApp API."""
    try:
        resultado = WhatsAppConfigService.probar_conexion()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/webhook-info', methods=['GET'])
def webhook_info():
    """Obtiene información del webhook de WhatsApp."""
    try:
        info = WhatsAppConfigService.obtener_webhook_info()
        return jsonify(info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/enviar-prueba', methods=['POST'])
def enviar_prueba():
    """Envía un mensaje de prueba."""
    try:
        data = request.get_json()
        numero = data.get('numero_destino')
        
        if not numero:
            return jsonify({'error': 'numero_destino requerido'}), 400
        
        resultado = WhatsAppConfigService.enviar_mensaje_prueba(numero)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/whatsapp/procesar-imagen', methods=['POST'])
def procesar_imagen():
    """Procesa una imagen recibida por WhatsApp."""
    try:
        data = request.get_json()
        media_id = data.get('media_id')
        sender_id = data.get('sender_id')
        tipo = data.get('tipo', 'factura')
        
        if not media_id or not sender_id:
            return jsonify({'error': 'media_id y sender_id requeridos'}), 400
        
        resultado = WhatsAppConfigService.procesar_imagen_recibida(
            media_id,
            sender_id,
            tipo
        )
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
