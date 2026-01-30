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
        email_provider = Config.EMAIL_PROVIDER.lower()
        
        config = {
            'email_provider': email_provider,
            'email_notificaciones_pedidos': Config.EMAIL_NOTIFICACIONES_PEDIDOS,
            'email_from': Config.EMAIL_FROM,
        }
        
        if email_provider == 'sendgrid':
            config.update({
                'sendgrid_api_key_configured': bool(Config.SENDGRID_API_KEY),
                'sendgrid_api_key_preview': (
                    Config.SENDGRID_API_KEY[:10] + '...' + Config.SENDGRID_API_KEY[-4:] 
                    if Config.SENDGRID_API_KEY and len(Config.SENDGRID_API_KEY) > 14 
                    else 'No configurado'
                ),
                'estado': 'configurado' if (Config.SENDGRID_API_KEY and Config.EMAIL_NOTIFICACIONES_PEDIDOS) else 'no_configurado'
            })
        elif email_provider == 'gmail':
            config.update({
                'gmail_user_configured': bool(Config.GMAIL_SMTP_USER),
                'gmail_user': Config.GMAIL_SMTP_USER,
                'gmail_password_configured': bool(Config.GMAIL_SMTP_PASSWORD),
                'gmail_smtp_server': Config.GMAIL_SMTP_SERVER,
                'gmail_smtp_port': Config.GMAIL_SMTP_PORT,
                'gmail_use_tls': Config.GMAIL_SMTP_USE_TLS,
                'estado': 'configurado' if (Config.GMAIL_SMTP_USER and Config.GMAIL_SMTP_PASSWORD and Config.EMAIL_NOTIFICACIONES_PEDIDOS) else 'no_configurado'
            })
        else:
            config['estado'] = 'no_configurado'
        
        return config
    
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
        email_provider = config.get('email_provider', 'sendgrid')
        
        if not config['email_notificaciones_pedidos']:
            return {
                'valido': False,
                'mensaje': 'Email de notificaciones no configurado',
                'detalles': 'Por favor, configura EMAIL_NOTIFICACIONES_PEDIDOS en las variables de entorno'
            }
        
        if email_provider == 'sendgrid':
            if not config.get('sendgrid_api_key_configured'):
                return {
                    'valido': False,
                    'mensaje': 'API Key de SendGrid no configurado',
                    'detalles': 'Por favor, configura SENDGRID_API_KEY en las variables de entorno'
                }
        elif email_provider == 'gmail':
            if not config.get('gmail_user_configured'):
                return {
                    'valido': False,
                    'mensaje': 'Usuario de Gmail no configurado',
                    'detalles': 'Por favor, configura GMAIL_SMTP_USER en las variables de entorno'
                }
            if not config.get('gmail_password_configured'):
                return {
                    'valido': False,
                    'mensaje': 'Contraseña de aplicación de Gmail no configurada',
                    'detalles': 'Por favor, configura GMAIL_SMTP_PASSWORD (contraseña de aplicación) en las variables de entorno'
                }
        
        # Verificar que el servicio de email funcione
        try:
            from modules.crm.notificaciones.email import email_service
            if email_provider == 'sendgrid':
                if email_service.sendgrid_client:
                    return {
                        'valido': True,
                        'mensaje': 'Configuración de SendGrid válida',
                        'detalles': f'Email de notificaciones: {config["email_notificaciones_pedidos"]}'
                    }
                else:
                    return {
                        'valido': False,
                        'mensaje': 'Servicio de SendGrid no inicializado',
                        'detalles': 'Verifica la configuración de SendGrid'
                    }
            elif email_provider == 'gmail':
                if email_service.gmail_user and email_service.gmail_password:
                    return {
                        'valido': True,
                        'mensaje': 'Configuración de Gmail SMTP válida',
                        'detalles': f'Email de notificaciones: {config["email_notificaciones_pedidos"]}, Usuario: {config.get("gmail_user", "N/A")}'
                    }
                else:
                    return {
                        'valido': False,
                        'mensaje': 'Servicio de Gmail SMTP no inicializado',
                        'detalles': 'Verifica la configuración de Gmail (usuario y contraseña de aplicación)'
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
