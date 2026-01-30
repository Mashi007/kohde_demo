"""
Políticas de configuración para WhatsApp Business API.
Define reglas y validaciones que deben cumplirse al configurar WhatsApp.
"""
import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse

class WhatsAppConfigPolicies:
    """Políticas y validaciones para configuración de WhatsApp."""
    
    # Políticas de formato
    MIN_PHONE_NUMBER_LENGTH = 10
    MAX_PHONE_NUMBER_LENGTH = 15
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 4096  # Límite de WhatsApp
    MIN_ACCESS_TOKEN_LENGTH = 20
    MAX_ACCESS_TOKEN_LENGTH = 500
    
    # Formatos válidos
    VALID_PHONE_NUMBER_PATTERN = re.compile(r'^\d{10,15}$')
    VALID_API_URL_PATTERN = re.compile(r'^https://graph\.facebook\.com/v\d+\.\d+$')
    
    @staticmethod
    def validar_numero_telefono(numero: str) -> Tuple[bool, str]:
        """
        Valida el formato de un número de teléfono.
        
        Args:
            numero: Número de teléfono a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not numero:
            return False, "El número de teléfono es requerido"
        
        # Eliminar espacios y caracteres especiales comunes
        numero_limpio = numero.strip().replace('+', '').replace('-', '').replace(' ', '')
        
        if not numero_limpio:
            return False, "El número de teléfono no puede estar vacío"
        
        if not numero_limpio.isdigit():
            return False, "El número de teléfono solo puede contener dígitos"
        
        if len(numero_limpio) < WhatsAppConfigPolicies.MIN_PHONE_NUMBER_LENGTH:
            return False, f"El número debe tener al menos {WhatsAppConfigPolicies.MIN_PHONE_NUMBER_LENGTH} dígitos"
        
        if len(numero_limpio) > WhatsAppConfigPolicies.MAX_PHONE_NUMBER_LENGTH:
            return False, f"El número no puede tener más de {WhatsAppConfigPolicies.MAX_PHONE_NUMBER_LENGTH} dígitos"
        
        if not WhatsAppConfigPolicies.VALID_PHONE_NUMBER_PATTERN.match(numero_limpio):
            return False, "El formato del número de teléfono no es válido"
        
        return True, ""
    
    @staticmethod
    def validar_mensaje(mensaje: str) -> Tuple[bool, str]:
        """
        Valida el contenido de un mensaje.
        
        Args:
            mensaje: Mensaje a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not mensaje:
            return False, "El mensaje es requerido"
        
        if len(mensaje.strip()) < WhatsAppConfigPolicies.MIN_MESSAGE_LENGTH:
            return False, "El mensaje no puede estar vacío"
        
        if len(mensaje) > WhatsAppConfigPolicies.MAX_MESSAGE_LENGTH:
            return False, f"El mensaje no puede exceder {WhatsAppConfigPolicies.MAX_MESSAGE_LENGTH} caracteres"
        
        return True, ""
    
    @staticmethod
    def validar_access_token(token: str) -> Tuple[bool, str]:
        """
        Valida el formato de un access token.
        
        Args:
            token: Token a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not token:
            return False, "El access token es requerido"
        
        if len(token) < WhatsAppConfigPolicies.MIN_ACCESS_TOKEN_LENGTH:
            return False, f"El token debe tener al menos {WhatsAppConfigPolicies.MIN_ACCESS_TOKEN_LENGTH} caracteres"
        
        if len(token) > WhatsAppConfigPolicies.MAX_ACCESS_TOKEN_LENGTH:
            return False, f"El token no puede exceder {WhatsAppConfigPolicies.MAX_ACCESS_TOKEN_LENGTH} caracteres"
        
        # Verificar que no contenga espacios
        if ' ' in token:
            return False, "El token no puede contener espacios"
        
        return True, ""
    
    @staticmethod
    def validar_phone_number_id(phone_id: str) -> Tuple[bool, str]:
        """
        Valida el formato de un Phone Number ID.
        
        Args:
            phone_id: Phone Number ID a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not phone_id:
            return False, "El Phone Number ID es requerido"
        
        if not phone_id.isdigit():
            return False, "El Phone Number ID solo puede contener dígitos"
        
        if len(phone_id) < 10:
            return False, "El Phone Number ID debe tener al menos 10 dígitos"
        
        return True, ""
    
    @staticmethod
    def validar_api_url(url: str) -> Tuple[bool, str]:
        """
        Valida el formato de la URL de la API de WhatsApp.
        
        Args:
            url: URL a validar
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not url:
            return False, "La URL de la API es requerida"
        
        try:
            parsed = urlparse(url)
            if parsed.scheme != 'https':
                return False, "La URL debe usar HTTPS"
            
            if not parsed.netloc:
                return False, "La URL debe tener un dominio válido"
            
            # Verificar que sea de Facebook Graph API
            if 'graph.facebook.com' not in parsed.netloc:
                return False, "La URL debe ser de Facebook Graph API (graph.facebook.com)"
            
            # Verificar formato de versión
            if not WhatsAppConfigPolicies.VALID_API_URL_PATTERN.match(url):
                return False, "La URL debe seguir el formato: https://graph.facebook.com/vXX.X"
            
        except Exception as e:
            return False, f"URL inválida: {str(e)}"
        
        return True, ""
    
    @staticmethod
    def validar_configuracion_completa(config: Dict) -> Tuple[bool, List[str]]:
        """
        Valida una configuración completa de WhatsApp.
        
        Args:
            config: Diccionario con la configuración
            
        Returns:
            Tupla (es_valido, lista_errores)
        """
        errores = []
        
        # Validar Access Token
        access_token = config.get('whatsapp_access_token') or config.get('WHATSAPP_ACCESS_TOKEN', '')
        es_valido, mensaje = WhatsAppConfigPolicies.validar_access_token(access_token)
        if not es_valido:
            errores.append(f"Access Token: {mensaje}")
        
        # Validar Phone Number ID
        phone_id = config.get('whatsapp_phone_number_id') or config.get('WHATSAPP_PHONE_NUMBER_ID', '')
        es_valido, mensaje = WhatsAppConfigPolicies.validar_phone_number_id(phone_id)
        if not es_valido:
            errores.append(f"Phone Number ID: {mensaje}")
        
        # Validar API URL (opcional, tiene valor por defecto)
        api_url = config.get('whatsapp_api_url') or config.get('WHATSAPP_API_URL', '')
        if api_url:
            es_valido, mensaje = WhatsAppConfigPolicies.validar_api_url(api_url)
            if not es_valido:
                errores.append(f"API URL: {mensaje}")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def sanitizar_numero_telefono(numero: str) -> str:
        """
        Sanitiza un número de teléfono eliminando caracteres especiales.
        
        Args:
            numero: Número de teléfono a sanitizar
            
        Returns:
            Número sanitizado (solo dígitos)
        """
        if not numero:
            return ""
        
        # Eliminar espacios y caracteres especiales
        numero_limpio = numero.strip().replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        return numero_limpio
    
    @staticmethod
    def obtener_politicas() -> Dict:
        """
        Obtiene todas las políticas de configuración.
        
        Returns:
            Diccionario con las políticas
        """
        return {
            'numero_telefono': {
                'min_longitud': WhatsAppConfigPolicies.MIN_PHONE_NUMBER_LENGTH,
                'max_longitud': WhatsAppConfigPolicies.MAX_PHONE_NUMBER_LENGTH,
                'formato': 'Solo dígitos, sin espacios ni caracteres especiales',
                'ejemplo': '521234567890'
            },
            'mensaje': {
                'min_longitud': WhatsAppConfigPolicies.MIN_MESSAGE_LENGTH,
                'max_longitud': WhatsAppConfigPolicies.MAX_MESSAGE_LENGTH,
                'formato': 'Texto plano',
                'nota': 'WhatsApp limita los mensajes a 4096 caracteres'
            },
            'access_token': {
                'min_longitud': WhatsAppConfigPolicies.MIN_ACCESS_TOKEN_LENGTH,
                'max_longitud': WhatsAppConfigPolicies.MAX_ACCESS_TOKEN_LENGTH,
                'formato': 'Token de acceso de Facebook Graph API',
                'seguridad': 'No debe exponerse en logs ni respuestas públicas'
            },
            'phone_number_id': {
                'min_longitud': 10,
                'formato': 'Solo dígitos',
                'descripcion': 'ID del número de teléfono de WhatsApp Business'
            },
            'api_url': {
                'formato': 'https://graph.facebook.com/vXX.X',
                'ejemplo': 'https://graph.facebook.com/v18.0',
                'requisito': 'Debe usar HTTPS'
            }
        }
