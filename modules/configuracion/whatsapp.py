"""
Servicio de configuración para WhatsApp Business API.
"""
import os
import requests
from typing import Dict, Optional, List
from werkzeug.utils import secure_filename
from pathlib import Path
from config import Config
from modules.crm.notificaciones.whatsapp import whatsapp_service

class WhatsAppConfigService:
    """Servicio para configurar y gestionar WhatsApp."""
    
    @staticmethod
    def verificar_configuracion() -> Dict:
        """
        Verifica que la configuración de WhatsApp esté completa.
        
        Returns:
            Diccionario con el estado de la configuración
        """
        config = {
            'api_url': Config.WHATSAPP_API_URL,
            'access_token': '✅ Configurado' if Config.WHATSAPP_ACCESS_TOKEN else '❌ No configurado',
            'phone_number_id': Config.WHATSAPP_PHONE_NUMBER_ID if Config.WHATSAPP_PHONE_NUMBER_ID else '❌ No configurado',
            'verify_token': '✅ Configurado' if Config.WHATSAPP_VERIFY_TOKEN else '❌ No configurado',
            'webhook_url': f"{Config.WHATSAPP_API_URL}/webhook",
            'completo': all([
                Config.WHATSAPP_ACCESS_TOKEN,
                Config.WHATSAPP_PHONE_NUMBER_ID,
                Config.WHATSAPP_VERIFY_TOKEN
            ])
        }
        return config
    
    @staticmethod
    def probar_conexion() -> Dict:
        """
        Prueba la conexión con WhatsApp API.
        
        Returns:
            Resultado de la prueba
        """
        try:
            if not Config.WHATSAPP_ACCESS_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
                return {
                    'exito': False,
                    'mensaje': 'Configuración incompleta'
                }
            
            # Intentar obtener información del número de teléfono
            url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}"
            headers = {
                "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'exito': True,
                    'mensaje': 'Conexión exitosa',
                    'datos': {
                        'display_phone_number': data.get('display_phone_number'),
                        'quality_rating': data.get('quality_rating', {}).get('rating', 'N/A')
                    }
                }
            else:
                return {
                    'exito': False,
                    'mensaje': f'Error: {response.status_code}',
                    'detalles': response.text
                }
                
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def descargar_imagen_whatsapp(media_id: str) -> Optional[str]:
        """
        Descarga una imagen desde WhatsApp API.
        
        Args:
            media_id: ID del medio en WhatsApp
            
        Returns:
            Ruta del archivo descargado o None
        """
        try:
            # Obtener URL del medio
            url = f"{Config.WHATSAPP_API_URL}/{media_id}"
            headers = {
                "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Error al obtener URL del medio: {response.status_code}")
                return None
            
            media_data = response.json()
            media_url = media_data.get('url')
            
            if not media_url:
                print("No se encontró URL del medio")
                return None
            
            # Descargar la imagen
            image_response = requests.get(media_url, headers=headers, timeout=30)
            
            if image_response.status_code != 200:
                print(f"Error al descargar imagen: {image_response.status_code}")
                return None
            
            # Determinar extensión del archivo
            content_type = media_data.get('mime_type', 'image/jpeg')
            extension = '.jpg'
            if 'png' in content_type:
                extension = '.png'
            elif 'pdf' in content_type:
                extension = '.pdf'
            
            # Guardar archivo
            filename = f"whatsapp_{media_id}{extension}"
            filepath = Config.UPLOAD_FOLDER / filename
            
            # Asegurar que el directorio existe
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(image_response.content)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error al descargar imagen de WhatsApp: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def procesar_imagen_recibida(media_id: str, sender_id: str, tipo: str = 'factura') -> Dict:
        """
        Procesa una imagen recibida por WhatsApp.
        
        Args:
            media_id: ID del medio en WhatsApp
            sender_id: ID del remitente
            tipo: Tipo de imagen ('factura', 'documento', etc.)
            
        Returns:
            Resultado del procesamiento
        """
        try:
            # Descargar imagen
            filepath = WhatsAppConfigService.descargar_imagen_whatsapp(media_id)
            
            if not filepath:
                return {
                    'exito': False,
                    'mensaje': 'No se pudo descargar la imagen'
                }
            
            # Procesar según el tipo
            if tipo == 'factura':
                from modules.contabilidad.ingreso_facturas import FacturaService
                from models import db
                
                factura = FacturaService.procesar_factura_desde_imagen(
                    db.session,
                    filepath,
                    tipo='proveedor'
                )
                
                return {
                    'exito': True,
                    'mensaje': 'Factura procesada correctamente',
                    'factura_id': factura.id,
                    'numero_factura': factura.numero_factura,
                    'total': float(factura.total)
                }
            else:
                return {
                    'exito': True,
                    'mensaje': 'Imagen guardada',
                    'filepath': filepath
                }
                
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
            import traceback
            traceback.print_exc()
            return {
                'exito': False,
                'mensaje': f'Error al procesar: {str(e)}'
            }
    
    @staticmethod
    def obtener_webhook_info() -> Dict:
        """
        Obtiene información sobre el webhook configurado.
        
        Returns:
            Información del webhook
        """
        try:
            if not Config.WHATSAPP_ACCESS_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
                return {
                    'configurado': False,
                    'mensaje': 'WhatsApp no está configurado'
                }
            
            url = f"{Config.WHATSAPP_API_URL}/{Config.WHATSAPP_PHONE_NUMBER_ID}/subscribed_apps"
            headers = {
                "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'configurado': True,
                    'apps': data.get('data', [])
                }
            else:
                return {
                    'configurado': False,
                    'mensaje': f'Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'configurado': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    @staticmethod
    def enviar_mensaje_prueba(numero_destino: str) -> Dict:
        """
        Envía un mensaje de prueba.
        
        Args:
            numero_destino: Número de teléfono destino
            
        Returns:
            Resultado del envío
        """
        try:
            mensaje = (
                "✅ Prueba de configuración WhatsApp\n\n"
                "Este es un mensaje de prueba del sistema ERP.\n"
                "Si recibes este mensaje, la configuración está correcta."
            )
            
            resultado = whatsapp_service.enviar_mensaje(numero_destino, mensaje)
            
            return {
                'exito': True,
                'mensaje': 'Mensaje enviado correctamente',
                'whatsapp_id': resultado.get('messages', [{}])[0].get('id')
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error al enviar mensaje: {str(e)}'
            }
