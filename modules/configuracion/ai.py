"""
Lógica de negocio para configuración de AI (OpenAI).
"""
from typing import Dict, Optional
from config import Config

class AIConfigService:
    """Servicio para gestión de configuración de AI."""
    
    # Almacenamiento en memoria del token (temporal, se pierde al reiniciar)
    _token_en_memoria: Optional[str] = None
    _modelo_en_memoria: Optional[str] = None
    _base_url_en_memoria: Optional[str] = None
    
    @classmethod
    def obtener_api_key(cls) -> str:
        """Obtiene la API key, priorizando la de memoria sobre la de entorno."""
        return cls._token_en_memoria or Config.OPENAI_API_KEY
    
    @classmethod
    def obtener_modelo(cls) -> str:
        """Obtiene el modelo, priorizando el de memoria sobre el de entorno."""
        return cls._modelo_en_memoria or Config.OPENAI_MODEL
    
    @classmethod
    def obtener_base_url(cls) -> str:
        """Obtiene la base URL, priorizando la de memoria sobre la de entorno."""
        return cls._base_url_en_memoria or Config.OPENAI_BASE_URL
    
    @classmethod
    def actualizar_token(cls, api_key: str, modelo: Optional[str] = None, base_url: Optional[str] = None) -> Dict:
        """
        Actualiza el token de OpenAI en memoria.
        
        Args:
            api_key: Nueva API key
            modelo: Modelo a usar (opcional)
            base_url: Base URL (opcional)
            
        Returns:
            Diccionario con el resultado
        """
        if not api_key or not api_key.strip():
            return {
                'exito': False,
                'error': 'La API key no puede estar vacía'
            }
        
        # Validar formato básico del token (debe empezar con sk-)
        api_key_limpia = api_key.strip()
        if not api_key_limpia.startswith('sk-'):
            return {
                'exito': False,
                'error': 'El formato del token no es válido. Debe empezar con "sk-"'
            }
        
        if len(api_key_limpia) < 20:
            return {
                'exito': False,
                'error': 'El token es demasiado corto'
            }
        
        # Guardar en memoria
        cls._token_en_memoria = api_key_limpia
        
        if modelo:
            cls._modelo_en_memoria = modelo.strip()
        
        if base_url:
            cls._base_url_en_memoria = base_url.strip()
        
        return {
            'exito': True,
            'mensaje': 'Token actualizado correctamente',
            'nota': 'El token se guardó en memoria. Se perderá al reiniciar el servidor.'
        }
    
    @staticmethod
    def obtener_configuracion() -> Dict:
        """
        Obtiene la configuración actual de AI.
        
        Returns:
            Diccionario con la configuración
        """
        api_key = AIConfigService.obtener_api_key()
        modelo = AIConfigService.obtener_modelo()
        base_url = AIConfigService.obtener_base_url()
        
        return {
            'openai_api_key_configured': bool(api_key),
            'openai_api_key_preview': (
                api_key[:10] + '...' + api_key[-4:] 
                if api_key and len(api_key) > 14 
                else 'No configurado'
            ),
            'openai_model': modelo,
            'openai_base_url': base_url,
            'estado': 'configurado' if api_key else 'no_configurado',
            'token_en_memoria': AIConfigService._token_en_memoria is not None
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
                'detalles': 'Por favor, ingresa el token de OpenAI o configura OPENAI_API_KEY en las variables de entorno'
            }
        
        # Intentar una llamada de prueba simple
        try:
            import requests
            
            api_key = AIConfigService.obtener_api_key()
            base_url = AIConfigService.obtener_base_url()
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Llamada simple para verificar la API key
            response = requests.get(
                f"{base_url}/models",
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
        api_key = AIConfigService.obtener_api_key()
        modelo = AIConfigService.obtener_modelo()
        base_url = AIConfigService.obtener_base_url()
        
        if not api_key:
            return {
                'exito': False,
                'error': 'API Key de OpenAI no configurada'
            }
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": modelo,
                "messages": [
                    {"role": "system", "content": "Eres un asistente útil. Responde brevemente."},
                    {"role": "user", "content": mensaje}
                ],
                "max_tokens": 50
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
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
