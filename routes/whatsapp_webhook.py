"""
Webhook para recibir mensajes de WhatsApp Business API.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
from models import db
from config import Config
from modules.contabilidad.ingreso_facturas import FacturaService

bp = Blueprint('whatsapp', __name__)

@bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verifica el webhook de WhatsApp (requerido por Meta).
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == Config.WHATSAPP_VERIFY_TOKEN:
        return challenge, 200
    else:
        return jsonify({'error': 'Token inválido'}), 403

@bp.route('/webhook', methods=['POST'])
def receive_message():
    """
    Recibe mensajes y medios de WhatsApp.
    """
    try:
        data = request.get_json()
        
        # Verificar que es un mensaje válido
        if 'entry' not in data:
            return jsonify({'status': 'ok'}), 200
        
        for entry in data['entry']:
            if 'messaging' not in entry:
                continue
            
            for message in entry['messaging']:
                # Obtener número del remitente
                sender_id = message.get('from')
                
                # Si el mensaje tiene imagen (factura)
                if 'message' in message and 'image' in message['message']:
                    handle_image_message(sender_id, message['message']['image'])
                
                # Si el mensaje es texto
                elif 'message' in message and 'text' in message['message']:
                    handle_text_message(sender_id, message['message']['text'])
        
        return jsonify({'status': 'ok'}), 200
    
    except Exception as e:
        print(f"Error al procesar webhook: {e}")
        return jsonify({'error': str(e)}), 500

def handle_image_message(sender_id: str, image_data: dict):
    """
    Maneja mensajes con imágenes (facturas).
    
    Args:
        sender_id: ID del remitente
        image_data: Datos de la imagen del mensaje
    """
    try:
        # Obtener ID de la imagen
        image_id = image_data.get('id')
        
        if not image_id:
            return
        
        # Usar el servicio de configuración para procesar
        from modules.configuracion.whatsapp import WhatsAppConfigService
        
        resultado = WhatsAppConfigService.procesar_imagen_recibida(
            image_id,
            sender_id,
            tipo='factura'
        )
        
        if resultado.get('exito'):
            # Enviar confirmación al remitente
            from modules.notificaciones.whatsapp import whatsapp_service
            mensaje = (
                f"✅ Factura recibida\n\n"
                f"Número: {resultado.get('numero_factura', 'N/A')}\n"
                f"Total: ${resultado.get('total', 0):,.2f}\n\n"
                f"La factura está pendiente de aprobación en el sistema."
            )
            whatsapp_service.enviar_mensaje(sender_id, mensaje)
        else:
            # Enviar mensaje de error
            from modules.notificaciones.whatsapp import whatsapp_service
            whatsapp_service.enviar_mensaje(
                sender_id,
                f"❌ Error al procesar la factura: {resultado.get('mensaje', 'Error desconocido')}"
            )
        
    except Exception as e:
        print(f"Error al procesar imagen: {e}")
        import traceback
        traceback.print_exc()
        # Enviar mensaje de error al usuario
        try:
            from modules.notificaciones.whatsapp import whatsapp_service
            whatsapp_service.enviar_mensaje(
                sender_id,
                "❌ Error al procesar la factura. Por favor, intente nuevamente."
            )
        except:
            pass

def handle_text_message(sender_id: str, text: str):
    """
    Maneja mensajes de texto.
    
    Args:
        sender_id: ID del remitente
        text: Texto del mensaje
    """
    # Aquí puedes implementar comandos de texto si es necesario
    # Por ejemplo: "STOCK", "PEDIDOS", etc.
    pass

def download_image_from_whatsapp(image_id: str) -> str:
    """
    Descarga una imagen desde WhatsApp API.
    
    Args:
        image_id: ID de la imagen en WhatsApp
        
    Returns:
        URL temporal de la imagen o None
    """
    try:
        # Usar el servicio de configuración para descargar
        from modules.configuracion.whatsapp import WhatsAppConfigService
        filepath = WhatsAppConfigService.descargar_imagen_whatsapp(image_id)
        return filepath
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
        return None
