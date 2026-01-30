"""
Script de diagnóstico para verificar la configuración del chat AI.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from modules.configuracion.ai import AIConfigService

def main():
    """Ejecuta diagnóstico de configuración del chat."""
    print("=" * 70)
    print("DIAGNÓSTICO DE CONFIGURACIÓN DEL CHAT AI")
    print("=" * 70)
    print()
    
    # 1. Verificar variables de entorno
    print("📋 VARIABLES DE ENTORNO:")
    print("-" * 70)
    print(f"OPENAI_API_KEY: {'✅ Configurada' if Config.OPENAI_API_KEY else '❌ No configurada'}")
    if Config.OPENAI_API_KEY:
        print(f"  Valor: {Config.OPENAI_API_KEY[:20]}...{Config.OPENAI_API_KEY[-10:]}")
    
    print(f"OPENROUTER_API_KEY: {'✅ Configurada' if Config.OPENROUTER_API_KEY else '❌ No configurada'}")
    if Config.OPENROUTER_API_KEY:
        print(f"  Valor: {Config.OPENROUTER_API_KEY[:20]}...{Config.OPENROUTER_API_KEY[-10:]}")
    
    print(f"OPENAI_MODEL: {Config.OPENAI_MODEL}")
    print(f"OPENAI_BASE_URL: {Config.OPENAI_BASE_URL}")
    print(f"OPENROUTER_HTTP_REFERER: {Config.OPENROUTER_HTTP_REFERER}")
    print(f"OPENROUTER_X_TITLE: {Config.OPENROUTER_X_TITLE}")
    print()
    
    # 2. Verificar servicio de configuración AI
    print("🔧 SERVICIO DE CONFIGURACIÓN AI:")
    print("-" * 70)
    api_key = AIConfigService.obtener_api_key()
    model = AIConfigService.obtener_modelo()
    base_url = AIConfigService.obtener_base_url()
    
    print(f"API Key obtenida: {'✅ Sí' if api_key else '❌ No'}")
    if api_key:
        print(f"  Valor: {api_key[:20]}...{api_key[-10:]}")
        # Detectar tipo de token
        if api_key.startswith('sk-or-v1-'):
            print(f"  Tipo: OpenRouter")
        elif api_key.startswith('sk-'):
            print(f"  Tipo: OpenAI")
        else:
            print(f"  Tipo: Desconocido")
    
    print(f"Modelo obtenido: {model}")
    print(f"Base URL obtenida: {base_url}")
    print()
    
    # 3. Verificar que el servicio de chat puede obtener credenciales
    print("💬 SERVICIO DE CHAT:")
    print("-" * 70)
    try:
        from modules.chat.chat_service import chat_service
        credenciales = chat_service._obtener_credenciales()
        
        print(f"API Key: {'✅ Sí' if credenciales['api_key'] else '❌ No'}")
        print(f"Modelo: {credenciales['model']}")
        print(f"Base URL: {credenciales['base_url']}")
        
        if not credenciales['api_key']:
            print()
            print("⚠️  PROBLEMA DETECTADO: No hay API key configurada")
            print()
            print("SOLUCIÓN:")
            print("1. Configura OPENROUTER_API_KEY o OPENAI_API_KEY en las variables de entorno")
            print("2. En Render.com:")
            print("   - Ve a tu servicio")
            print("   - Sección 'Environment'")
            print("   - Agrega: OPENROUTER_API_KEY=sk-or-v1-...")
            print("   - Agrega: OPENAI_MODEL=openai/gpt-3.5-turbo")
            print("   - Agrega: OPENAI_BASE_URL=https://openrouter.ai/api/v1")
            print("   - Reinicia el servicio")
        else:
            print()
            print("✅ Configuración correcta. El chat debería funcionar.")
            
    except Exception as e:
        print(f"❌ Error al verificar servicio de chat: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()
