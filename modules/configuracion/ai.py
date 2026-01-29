"""
Lógica de negocio para configuración de AI (OpenAI).
"""
from typing import Dict, Optional
from config import Config

class AIConfigService:
    """Servicio para gestión de configuración de AI."""
    
    @staticmethod
    def obtener_configuracion() -> Dict:
        """
        Obtiene la configuración actual de AI.
        
        Returns:
            Diccionario con la configuración
        """
        return {
            'openai_api_key_configured': bool(Config.OPENAI_API_KEY),
            'openai_api_key_preview': (
                Config.OPENAI_API_KEY[:10] + '...' + Config.OPENAI_API_KEY[-4:] 
                if Config.OPENAI_API_KEY and len(Config.OPENAI_API_KEY) > 14 
                else 'No configurado'
            ),
            'openai_model': Config.OPENAI_MODEL,
            'openai_base_url': Config.OPENAI_BASE_URL,
            'estado': 'configurado' if Config.OPENAI_API_KEY else 'no_configurado'
        }
    
    @staticmethod
    def verificar_configuracion() -> Dict:
        """
        Verifica si la configuración de AI es válida.
        
        Returns:
            Diccionario con el resultado de la verificación
        """
        config = AIConfigService.obtener_configuracion()
        
        if not config['openai_api_key_configured']:
            return {
                'valido': False,
                'mensaje': 'API Key de OpenAI no configurada',
                'detalles': 'Por favor, configura OPENAI_API_KEY en las variables de entorno'
            }
        
        # Intentar una llamada de prueba simple
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Llamada simple para verificar la API key
            response = requests.get(
                f"{Config.OPENAI_BASE_URL}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'valido': True,
                    'mensaje': 'Configuración de AI válida',
                    'detalles': 'La API key de OpenAI está funcionando correctamente'
                }
            else:
                return {
                    'valido': False,
                    'mensaje': f'Error al verificar API key: {response.status_code}',
                    'detalles': response.text[:200]
                }
        except Exception as e:
            return {
                'valido': False,
                'mensaje': 'Error al verificar configuración',
                'detalles': str(e)
            }
    
    @staticmethod
    def enviar_mensaje_prueba(mensaje: str = "Hola, ¿puedes responder con 'OK'?") -> Dict:
        """
        Envía un mensaje de prueba al AI.
        
        Args:
            mensaje: Mensaje de prueba
            
        Returns:
            Diccionario con la respuesta
        """
        if not Config.OPENAI_API_KEY:
            return {
                'exito': False,
                'error': 'API Key de OpenAI no configurada'
            }
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": Config.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "Eres un asistente útil. Responde brevemente."},
                    {"role": "user", "content": mensaje}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(
                f"{Config.OPENAI_BASE_URL}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'exito': True,
                    'respuesta': result['choices'][0]['message']['content'],
                    'tokens_usados': result.get('usage', {}).get('total_tokens', 0)
                }
            else:
                return {
                    'exito': False,
                    'error': f'Error {response.status_code}: {response.text[:200]}'
                }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

# Instancia global del servicio
ai_config_service = AIConfigService()
