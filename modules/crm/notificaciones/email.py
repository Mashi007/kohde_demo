"""
Integración con SendGrid y Gmail SMTP para envío de emails.
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, List, Optional
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import Config

class EmailService:
    """Servicio para envío de emails (SendGrid o Gmail SMTP)."""
    
    def __init__(self):
        """Inicializa el servicio de email."""
        self.provider = Config.EMAIL_PROVIDER.lower()
        self.from_email = Config.EMAIL_FROM
        
        # SendGrid
        self.sendgrid_api_key = Config.SENDGRID_API_KEY
        self.sendgrid_client = None
        
        # Gmail SMTP
        self.gmail_user = Config.GMAIL_SMTP_USER
        self.gmail_password = Config.GMAIL_SMTP_PASSWORD
        self.gmail_smtp_server = Config.GMAIL_SMTP_SERVER
        self.gmail_smtp_port = Config.GMAIL_SMTP_PORT
        self.gmail_use_tls = Config.GMAIL_SMTP_USE_TLS
        
        # Inicializar según el proveedor configurado
        if self.provider == 'sendgrid' and self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
        elif self.provider == 'gmail' and self.gmail_user and self.gmail_password:
            # Gmail está configurado
            pass
    
    def enviar_email(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        contenido_texto: Optional[str] = None
    ) -> Dict:
        """
        Envía un email usando el proveedor configurado (SendGrid o Gmail SMTP).
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            contenido_html: Contenido HTML del email
            contenido_texto: Contenido de texto plano (opcional)
            
        Returns:
            Respuesta del servicio de email
        """
        if self.provider == 'sendgrid':
            return self._enviar_email_sendgrid(destinatario, asunto, contenido_html, contenido_texto)
        elif self.provider == 'gmail':
            return self._enviar_email_gmail(destinatario, asunto, contenido_html, contenido_texto)
        else:
            raise Exception(f"Proveedor de email no configurado: {self.provider}")
    
    def _enviar_email_sendgrid(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        contenido_texto: Optional[str] = None
    ) -> Dict:
        """Envía email usando SendGrid."""
        if not self.sendgrid_client:
            raise Exception("SendGrid no configurado correctamente")
        
        message = Mail(
            from_email=self.from_email,
            to_emails=destinatario,
            subject=asunto,
            html_content=contenido_html,
            plain_text_content=contenido_texto
        )
        
        try:
            response = self.sendgrid_client.send(message)
            return {
                'status_code': response.status_code,
                'body': response.body,
                'headers': response.headers,
                'provider': 'sendgrid'
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email con SendGrid: {e}", exc_info=True)
            raise
    
    def _enviar_email_gmail(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        contenido_texto: Optional[str] = None
    ) -> Dict:
        """Envía email usando Gmail SMTP."""
        if not self.gmail_user or not self.gmail_password:
            raise Exception("Gmail SMTP no configurado correctamente")
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_user
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            # Agregar contenido
            if contenido_texto:
                part1 = MIMEText(contenido_texto, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(contenido_html, 'html')
            msg.attach(part2)
            
            # Conectar y enviar
            if self.gmail_use_tls:
                server = smtplib.SMTP(self.gmail_smtp_server, self.gmail_smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.gmail_smtp_server, self.gmail_smtp_port)
            
            server.login(self.gmail_user, self.gmail_password)
            text = msg.as_string()
            server.sendmail(self.gmail_user, destinatario, text)
            server.quit()
            
            return {
                'status_code': 200,
                'mensaje': 'Email enviado correctamente',
                'provider': 'gmail'
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email con Gmail SMTP: {e}", exc_info=True)
            raise Exception(f"Error al enviar email con Gmail: {str(e)}")
    
    def enviar_factura(self, destinatario: str, factura_info: Dict) -> Dict:
        """
        Envía una factura por email.
        
        Args:
            destinatario: Email del destinatario
            factura_info: Información de la factura
            
        Returns:
            Respuesta de SendGrid
        """
        html = f"""
        <html>
        <body>
            <h2>Factura {factura_info.get('numero_factura')}</h2>
            <p><strong>Proveedor:</strong> {factura_info.get('proveedor', 'N/A')}</p>
            <p><strong>Fecha:</strong> {factura_info.get('fecha_emision', 'N/A')}</p>
            <p><strong>Subtotal:</strong> ${factura_info.get('subtotal', 0):,.2f}</p>
            <p><strong>IVA:</strong> ${factura_info.get('iva', 0):,.2f}</p>
            <p><strong>Total:</strong> ${factura_info.get('total', 0):,.2f}</p>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatario,
            f"Factura {factura_info.get('numero_factura')}",
            html
        )
    
    def enviar_reporte_inventario(self, destinatario: str, items: List[Dict]) -> Dict:
        """
        Envía un reporte de inventario por email.
        
        Args:
            destinatario: Email del destinatario
            items: Lista de items del inventario
            
        Returns:
            Respuesta de SendGrid
        """
        html = "<html><body><h2>Reporte de Inventario</h2><table border='1'><tr><th>Item</th><th>Cantidad</th><th>Unidad</th></tr>"
        
        for item in items:
            html += f"<tr><td>{item.get('nombre')}</td><td>{item.get('cantidad_actual')}</td><td>{item.get('unidad')}</td></tr>"
        
        html += "</table></body></html>"
        
        return self.enviar_email(
            destinatario,
            "Reporte de Inventario",
            html
        )
    
    def enviar_email_con_adjunto(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        archivo_adjunto: str
    ) -> Dict:
        """
        Envía un email con un archivo adjunto.
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            contenido_html: Contenido HTML del email
            archivo_adjunto: Ruta del archivo a adjuntar
            
        Returns:
            Respuesta del servicio de email
        """
        if self.provider == 'sendgrid':
            return self._enviar_email_con_adjunto_sendgrid(destinatario, asunto, contenido_html, archivo_adjunto)
        elif self.provider == 'gmail':
            return self._enviar_email_con_adjunto_gmail(destinatario, asunto, contenido_html, archivo_adjunto)
        else:
            raise Exception(f"Proveedor de email no configurado: {self.provider}")
    
    def _enviar_email_con_adjunto_sendgrid(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        archivo_adjunto: str
    ) -> Dict:
        """Envía email con adjunto usando SendGrid."""
        if not self.sendgrid_client:
            raise Exception("SendGrid no configurado correctamente")
        
        message = Mail(
            from_email=self.from_email,
            to_emails=destinatario,
            subject=asunto,
            html_content=contenido_html
        )
        
        # Adjuntar archivo
        with open(archivo_adjunto, 'rb') as f:
            data = f.read()
            message.add_attachment(
                data,
                main_type='application',
                sub_type='pdf',
                filename=Path(archivo_adjunto).name
            )
        
        try:
            response = self.sendgrid_client.send(message)
            return {
                'status_code': response.status_code,
                'body': response.body,
                'headers': response.headers
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email con adjunto: {e}", exc_info=True)
            raise
    
    def _enviar_email_con_adjunto_gmail(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        archivo_adjunto: str
    ) -> Dict:
        """Envía email con adjunto usando Gmail SMTP."""
        if not self.gmail_user or not self.gmail_password:
            raise Exception("Gmail SMTP no configurado correctamente")
        
        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.gmail_user
            msg['To'] = destinatario
            msg['Subject'] = asunto
            
            # Agregar contenido HTML
            part1 = MIMEText(contenido_html, 'html')
            msg.attach(part1)
            
            # Adjuntar archivo
            with open(archivo_adjunto, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(archivo_adjunto).name}'
                )
                msg.attach(part)
            
            # Conectar y enviar
            if self.gmail_use_tls:
                server = smtplib.SMTP(self.gmail_smtp_server, self.gmail_smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.gmail_smtp_server, self.gmail_smtp_port)
            
            server.login(self.gmail_user, self.gmail_password)
            text = msg.as_string()
            server.sendmail(self.gmail_user, destinatario, text)
            server.quit()
            
            return {
                'status_code': 200,
                'mensaje': 'Email con adjunto enviado correctamente',
                'provider': 'gmail'
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email con adjunto usando Gmail: {e}", exc_info=True)
            raise Exception(f"Error al enviar email con adjunto usando Gmail: {str(e)}")
    
    def enviar_resumen_tickets(self, destinatario: str, tickets: List[Dict]) -> Dict:
        """
        Envía un resumen de tickets por email.
        
        Args:
            destinatario: Email del destinatario
            tickets: Lista de tickets
            
        Returns:
            Respuesta de SendGrid
        """
        html = "<html><body><h2>Resumen de Tickets</h2><ul>"
        
        for ticket in tickets:
            html += f"<li><strong>{ticket.get('asunto')}</strong> - {ticket.get('estado')}</li>"
        
        html += "</ul></body></html>"
        
        return self.enviar_email(
            destinatario,
            "Resumen de Tickets",
            html
        )

    @property
    def client(self):
        """Propiedad para compatibilidad con código existente."""
        return self.sendgrid_client if self.provider == 'sendgrid' else None

# Instancia global
email_service = EmailService()
