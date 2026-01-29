"""
Webhook para recibir mensajes de WhatsApp Business API.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import requests
from models import db
from config import Config
from modules.logistica.facturas import FacturaService
from modules.logistica.facturas_whatsapp import FacturasWhatsAppService
from modules.crm.notificaciones.whatsapp import whatsapp_service
from modules.configuracion.whatsapp import WhatsAppConfigService

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
                
                if 'message' not in message:
                    continue
                
                msg = message['message']
                
                # Obtener nombre del remitente si está disponible
                sender_name = message.get('profile', {}).get('name')
                
                # Si el mensaje tiene imagen (factura)
                if 'image' in msg:
                    handle_image_message(sender_id, msg['image'], sender_name)
                
                # Si el mensaje tiene documento (PDF, etc.)
                elif 'document' in msg:
                    # Tratar documentos como imágenes para OCR
                    handle_image_message(sender_id, msg['document'], sender_name)
                
                # Si el mensaje es texto
                elif 'text' in msg:
                    handle_text_message(sender_id, msg['text'])
        
        return jsonify({'status': 'ok'}), 200
    
    except Exception as e:
        print(f"Error al procesar webhook: {e}")
        return jsonify({'error': str(e)}), 500

def handle_image_message(sender_id: str, image_data: dict, sender_name: str = None):
    """
    Maneja mensajes con imágenes (facturas).
    
    Args:
        sender_id: ID del remitente (teléfono)
        image_data: Datos de la imagen del mensaje
        sender_name: Nombre del remitente (opcional)
    """
    try:
        # Obtener ID de la imagen
        image_id = image_data.get('id')
        
        if not image_id:
            return
        
        # Procesar factura desde WhatsApp
        resultado = FacturasWhatsAppService.procesar_factura_desde_whatsapp(
            db.session,
            image_id,
            sender_id,
            sender_name
        )
        
        if resultado.get('exito'):
            # Enviar confirmación al remitente
            mensaje = (
                f"✅ Factura recibida y procesada\n\n"
                f"Número: {resultado.get('numero_factura', 'N/A')}\n"
                f"Proveedor: {resultado.get('proveedor', 'No identificado')}\n"
                f"Total: ${resultado.get('total', 0):,.2f}\n"
                f"Items detectados: {resultado.get('items', 0)}\n\n"
                f"La factura está pendiente de confirmación en el sistema."
            )
            whatsapp_service.enviar_mensaje(sender_id, mensaje)
        else:
            # Enviar mensaje de error
            whatsapp_service.enviar_mensaje(
                sender_id,
                f"❌ Error al procesar la factura: {resultado.get('mensaje', 'Error desconocido')}\n\n"
                f"Por favor, verifica que la imagen sea clara y contenga información de factura."
            )
        
    except Exception as e:
        print(f"Error al procesar imagen: {e}")
        import traceback
        traceback.print_exc()
        # Enviar mensaje de error al usuario
        try:
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
        filepath = WhatsAppConfigService.descargar_imagen_whatsapp(image_id)
        return filepath
    except Exception as e:
        print(f"Error al descargar imagen: {e}")
        return None
