"""
Lógica de negocio para configuración de notificaciones por email.
"""
from typing import Dict
from config import Config

class NotificacionesConfigService:
    """Servicio para gestión de configuración de notificaciones por email."""
    
    @staticmethod
    def obtener_configuracion() -> Dict:
        """
        Obtiene la configuración actual de notificaciones por email.
        
        Returns:
            Diccionario con la configuración
        """
        return {
            'email_notificaciones_pedidos': Config.EMAIL_NOTIFICACIONES_PEDIDOS,
            'email_from': Config.EMAIL_FROM,
            'sendgrid_api_key_configured': bool(Config.SENDGRID_API_KEY),
            'sendgrid_api_key_preview': (
                Config.SENDGRID_API_KEY[:10] + '...' + Config.SENDGRID_API_KEY[-4:] 
                if Config.SENDGRID_API_KEY and len(Config.SENDGRID_API_KEY) > 14 
                else 'No configurado'
            ),
            'estado': 'configurado' if (Config.SENDGRID_API_KEY and Config.EMAIL_NOTIFICACIONES_PEDIDOS) else 'no_configurado'
        }
    
    @staticmethod
    def actualizar_email_notificaciones(email: str) -> Dict:
        """
        Actualiza el email de notificaciones de pedidos.
        Nota: En producción, esto debería actualizar una variable de entorno o base de datos.
        Por ahora, solo valida el formato.
        
        Args:
            email: Email para notificaciones de pedidos
            
        Returns:
            Diccionario con el resultado
        """
        import re
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                'exito': False,
                'error': 'Formato de email inválido'
            }
        
        # En producción, aquí se actualizaría la variable de entorno o base de datos
        # Por ahora, solo retornamos éxito
        # TODO: Implementar actualización persistente de configuración
        return {
            'exito': True,
            'mensaje': f'Email de notificaciones actualizado a: {email}',
            'email': email,
            'nota': 'En producción, actualiza la variable de entorno EMAIL_NOTIFICACIONES_PEDIDOS'
        }
    
    @staticmethod
    def verificar_configuracion() -> Dict:
        """
        Verifica si la configuración de notificaciones es válida.
        
        Returns:
            Diccionario con el resultado de la verificación
        """
        config = NotificacionesConfigService.obtener_configuracion()
        
        if not config['sendgrid_api_key_configured']:
            return {
                'valido': False,
                'mensaje': 'API Key de SendGrid no configurado',
                'detalles': 'Por favor, configura SENDGRID_API_KEY en las variables de entorno'
            }
        
        if not config['email_notificaciones_pedidos']:
            return {
                'valido': False,
                'mensaje': 'Email de notificaciones no configurado',
                'detalles': 'Por favor, configura EMAIL_NOTIFICACIONES_PEDIDOS en las variables de entorno'
            }
        
        # Verificar que el servicio de email funcione
        try:
            from modules.crm.notificaciones.email import email_service
            # Solo verificamos que el servicio esté inicializado
            if email_service.client:
                return {
                    'valido': True,
                    'mensaje': 'Configuración válida',
                    'detalles': f'Email de notificaciones: {config["email_notificaciones_pedidos"]}'
                }
            else:
                return {
                    'valido': False,
                    'mensaje': 'Servicio de email no inicializado',
                    'detalles': 'Verifica la configuración de SendGrid'
                }
        except Exception as e:
            return {
                'valido': False,
                'mensaje': 'Error al verificar configuración',
                'detalles': str(e)
            }
    
    @staticmethod
    def enviar_email_prueba(email_destino: str = None) -> Dict:
        """
        Envía un email de prueba.
        
        Args:
            email_destino: Email destino (opcional, usa el configurado si no se proporciona)
            
        Returns:
            Diccionario con el resultado
        """
        try:
            from modules.crm.notificaciones.email import email_service
            
            email_destino = email_destino or Config.EMAIL_NOTIFICACIONES_PEDIDOS
            
            if not email_destino:
                return {
                    'exito': False,
                    'error': 'Email de destino no especificado'
                }
            
            contenido_html = """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #7C3AED;">Email de Prueba</h2>
                    <p>Este es un email de prueba del sistema ERP de restaurantes.</p>
                    <p>Si recibes este correo, la configuración de notificaciones está funcionando correctamente.</p>
                </div>
            </body>
            </html>
            """
            
            resultado = email_service.enviar_email(
                email_destino,
                'Prueba de Notificaciones - ERP Restaurantes',
                contenido_html
            )
            
            return {
                'exito': True,
                'mensaje': 'Email de prueba enviado correctamente',
                'status_code': resultado.get('status_code')
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

# Instancia global del servicio
notificaciones_config_service = NotificacionesConfigService()
