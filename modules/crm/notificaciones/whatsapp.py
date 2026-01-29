"""
Integración con WhatsApp Business API.
"""
import requests
from typing import Dict, Optional
from config import Config

class WhatsAppService:
    """Servicio para envío de mensajes por WhatsApp."""
    
    def __init__(self):
        """Inicializa el servicio de WhatsApp."""
        self.api_url = Config.WHATSAPP_API_URL
        self.access_token = Config.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
    
    def enviar_mensaje(self, numero_destino: str, mensaje: str) -> Dict:
        """
        Envía un mensaje de texto por WhatsApp.
        
        Args:
            numero_destino: Número de teléfono destino (formato: 593999999999)
            mensaje: Mensaje a enviar
            
        Returns:
            Respuesta de la API
        """
        if not self.access_token or not self.phone_number_id:
            raise Exception("WhatsApp no configurado correctamente")
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": numero_destino,
            "type": "text",
            "text": {
                "body": mensaje
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar mensaje WhatsApp: {e}")
            raise
    
    def enviar_imagen(self, numero_destino: str, imagen_url: str, caption: Optional[str] = None) -> Dict:
        """
        Envía una imagen por WhatsApp.
        
        Args:
            numero_destino: Número de teléfono destino
            imagen_url: URL de la imagen
            caption: Texto opcional que acompaña la imagen
            
        Returns:
            Respuesta de la API
        """
        if not self.access_token or not self.phone_number_id:
            raise Exception("WhatsApp no configurado correctamente")
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": numero_destino,
            "type": "image",
            "image": {
                "link": imagen_url
            }
        }
        
        if caption:
            payload["image"]["caption"] = caption
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar imagen WhatsApp: {e}")
            raise
    
    def notificar_factura_recibida(self, numero_destino: str, factura_info: Dict) -> Dict:
        """
        Notifica la recepción de una nueva factura.
        
        Args:
            numero_destino: Número de teléfono destino
            factura_info: Información de la factura
            
        Returns:
            Respuesta de la API
        """
        mensaje = (
            f"📄 Nueva factura recibida\n\n"
            f"Proveedor: {factura_info.get('proveedor', 'N/A')}\n"
            f"Número: {factura_info.get('numero_factura', 'N/A')}\n"
            f"Total: ${factura_info.get('total', 0):,.2f}\n\n"
            f"Revisar en el sistema para aprobación."
        )
        return self.enviar_mensaje(numero_destino, mensaje)
    
    def notificar_ticket_resuelto(self, numero_destino: str, ticket_info: Dict) -> Dict:
        """
        Notifica que un ticket ha sido resuelto.
        
        Args:
            numero_destino: Número de teléfono destino
            ticket_info: Información del ticket
            
        Returns:
            Respuesta de la API
        """
        mensaje = (
            f"✅ Ticket resuelto\n\n"
            f"Asunto: {ticket_info.get('asunto', 'N/A')}\n"
            f"Respuesta: {ticket_info.get('respuesta', 'N/A')}\n\n"
            f"Gracias por contactarnos."
        )
        return self.enviar_mensaje(numero_destino, mensaje)
    
    def notificar_stock_bajo(self, numero_destino: str, items: list) -> Dict:
        """
        Notifica items con stock bajo.
        
        Args:
            numero_destino: Número de teléfono destino
            items: Lista de items con stock bajo
            
        Returns:
            Respuesta de la API
        """
        mensaje = "⚠️ ALERTA: Stock bajo\n\n"
        for item in items[:5]:  # Limitar a 5 items
            mensaje += f"• {item.get('nombre')}: {item.get('cantidad_actual')} {item.get('unidad')}\n"
        
        if len(items) > 5:
            mensaje += f"\n... y {len(items) - 5} más.\n"
        
        mensaje += "\nRevisar en el sistema."
        return self.enviar_mensaje(numero_destino, mensaje)
    
    def notificar_pedido_generado(self, numero_destino: str, pedido_info: Dict) -> Dict:
        """
        Notifica la generación de un pedido automático.
        
        Args:
            numero_destino: Número de teléfono destino
            pedido_info: Información del pedido
            
        Returns:
            Respuesta de la API
        """
        mensaje = (
            f"🛒 Pedido automático generado\n\n"
            f"Proveedor: {pedido_info.get('proveedor', 'N/A')}\n"
            f"Total: ${pedido_info.get('total', 0):,.2f}\n"
            f"Items: {pedido_info.get('cantidad_items', 0)}\n\n"
            f"Revisar y enviar al proveedor."
        )
        return self.enviar_mensaje(numero_destino, mensaje)

# Instancia global
whatsapp_service = WhatsAppService()
