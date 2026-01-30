"""
Lógica de negocio para configuración de WhatsApp.
"""
from typing import Dict
from modules.crm.notificaciones.whatsapp import whatsapp_service
from modules.configuracion.whatsapp_policies import WhatsAppConfigPolicies
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
        Verifica si la configuración de WhatsApp es válida respetando las políticas.
        
        Returns:
            Diccionario con el resultado de la verificación
        """
        config = WhatsAppConfigService.obtener_configuracion()
        
        # Validar según políticas
        config_dict = {
            'WHATSAPP_ACCESS_TOKEN': Config.WHATSAPP_ACCESS_TOKEN,
            'WHATSAPP_PHONE_NUMBER_ID': Config.WHATSAPP_PHONE_NUMBER_ID,
            'WHATSAPP_API_URL': Config.WHATSAPP_API_URL
        }
        
        es_valido, errores = WhatsAppConfigPolicies.validar_configuracion_completa(config_dict)
        
        if not es_valido:
            return {
                'valido': False,
                'mensaje': 'Configuración inválida según políticas',
                'detalles': '; '.join(errores),
                'errores': errores
            }
        
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
        Envía un mensaje de prueba respetando las políticas de configuración.
        
        Args:
            numero: Número de teléfono destino (formato internacional sin +)
            mensaje: Mensaje de prueba
            
        Returns:
            Diccionario con el resultado
        """
        # Validar número según políticas
        es_valido, error_numero = WhatsAppConfigPolicies.validar_numero_telefono(numero)
        if not es_valido:
            return {
                'exito': False,
                'error': f'Número inválido: {error_numero}',
                'tipo_error': 'validacion_numero'
            }
        
        # Sanitizar número
        numero_sanitizado = WhatsAppConfigPolicies.sanitizar_numero_telefono(numero)
        
        # Validar mensaje según políticas
        es_valido, error_mensaje = WhatsAppConfigPolicies.validar_mensaje(mensaje)
        if not es_valido:
            return {
                'exito': False,
                'error': f'Mensaje inválido: {error_mensaje}',
                'tipo_error': 'validacion_mensaje'
            }
        
        try:
            resultado = whatsapp_service.enviar_mensaje(numero_sanitizado, mensaje)
            return {
                'exito': True,
                'mensaje_id': resultado.get('mensaje_id'),
                'mensaje': 'Mensaje enviado correctamente',
                'numero_usado': numero_sanitizado
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'tipo_error': 'error_envio'
            }
    
    @staticmethod
    def obtener_politicas() -> Dict:
        """
        Obtiene las políticas de configuración de WhatsApp.
        
        Returns:
            Diccionario con las políticas
        """
        return WhatsAppConfigPolicies.obtener_politicas()

# Instancia global del servicio
whatsapp_config_service = WhatsAppConfigService()
