"""
Integración con SendGrid para envío de emails.
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, List, Optional
from config import Config

class EmailService:
    """Servicio para envío de emails."""
    
    def __init__(self):
        """Inicializa el servicio de email."""
        self.api_key = Config.SENDGRID_API_KEY
        self.from_email = Config.EMAIL_FROM
        self.client = None
        
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
    
    def enviar_email(
        self,
        destinatario: str,
        asunto: str,
        contenido_html: str,
        contenido_texto: Optional[str] = None
    ) -> Dict:
        """
        Envía un email.
        
        Args:
            destinatario: Email del destinatario
            asunto: Asunto del email
            contenido_html: Contenido HTML del email
            contenido_texto: Contenido de texto plano (opcional)
            
        Returns:
            Respuesta de SendGrid
        """
        if not self.client:
            raise Exception("SendGrid no configurado correctamente")
        
        message = Mail(
            from_email=self.from_email,
            to_emails=destinatario,
            subject=asunto,
            html_content=contenido_html,
            plain_text_content=contenido_texto
        )
        
        try:
            response = self.client.send(message)
            return {
                'status_code': response.status_code,
                'body': response.body,
                'headers': response.headers
            }
        except Exception as e:
            print(f"Error al enviar email: {e}")
            raise
    
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

# Instancia global
email_service = EmailService()
