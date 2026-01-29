"""
Lógica de negocio para configuración de WhatsApp.
"""
from typing import Dict
from modules.crm.notificaciones.whatsapp import whatsapp_service
from config import Config

class WhatsAppConfigService:
    """Servicio para gestión de configuración de WhatsApp."""
    
    @staticmethod
    def obtener_configuracion() -> Dict:
        """
        Obtiene la configuración actual de WhatsApp.
        
        Returns:
            Diccionario con la configuración
        """
        return {
            'whatsapp_api_url': Config.WHATSAPP_API_URL,
            'whatsapp_phone_number_id_configured': bool(Config.WHATSAPP_PHONE_NUMBER_ID),
            'whatsapp_phone_number_id': Config.WHATSAPP_PHONE_NUMBER_ID,
            'whatsapp_access_token_configured': bool(Config.WHATSAPP_ACCESS_TOKEN),
            'whatsapp_access_token_preview': (
                Config.WHATSAPP_ACCESS_TOKEN[:10] + '...' + Config.WHATSAPP_ACCESS_TOKEN[-4:] 
                if Config.WHATSAPP_ACCESS_TOKEN and len(Config.WHATSAPP_ACCESS_TOKEN) > 14 
                else 'No configurado'
            ),
            'whatsapp_verify_token': Config.WHATSAPP_VERIFY_TOKEN,
            'estado': 'configurado' if (Config.WHATSAPP_ACCESS_TOKEN and Config.WHATSAPP_PHONE_NUMBER_ID) else 'no_configurado'
        }
    
    @staticmethod
    def verificar_configuracion() -> Dict:
        """
        Verifica si la configuración de WhatsApp es válida.
        
        Returns:
            Diccionario con el resultado de la verificación
        """
        config = WhatsAppConfigService.obtener_configuracion()
        
        if not config['whatsapp_access_token_configured']:
            return {
                'valido': False,
                'mensaje': 'Token de acceso de WhatsApp no configurado',
                'detalles': 'Por favor, configura WHATSAPP_ACCESS_TOKEN en las variables de entorno'
            }
        
        if not config['whatsapp_phone_number_id_configured']:
            return {
                'valido': False,
                'mensaje': 'Phone Number ID de WhatsApp no configurado',
                'detalles': 'Por favor, configura WHATSAPP_PHONE_NUMBER_ID en las variables de entorno'
            }
        
        # Intentar verificar con el servicio
        try:
            resultado = whatsapp_service.verificar_conexion()
            return {
                'valido': resultado.get('conectado', False),
                'mensaje': resultado.get('mensaje', 'Estado desconocido'),
                'detalles': resultado.get('detalles', '')
            }
        except Exception as e:
            return {
                'valido': False,
                'mensaje': 'Error al verificar configuración',
                'detalles': str(e)
            }
    
    @staticmethod
    def enviar_mensaje_prueba(numero: str, mensaje: str = "Mensaje de prueba desde ERP") -> Dict:
        """
        Envía un mensaje de prueba.
        
        Args:
            numero: Número de teléfono destino (formato internacional sin +)
            mensaje: Mensaje de prueba
            
        Returns:
            Diccionario con el resultado
        """
        try:
            resultado = whatsapp_service.enviar_mensaje(numero, mensaje)
            return {
                'exito': True,
                'mensaje_id': resultado.get('mensaje_id'),
                'mensaje': 'Mensaje enviado correctamente'
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

# Instancia global del servicio
whatsapp_config_service = WhatsAppConfigService()
