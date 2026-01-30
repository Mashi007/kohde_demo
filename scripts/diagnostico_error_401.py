"""
Script de diagnóstico para el error 401 "User not found" de OpenRouter.
"""
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from modules.configuracion.ai import AIConfigService

def verificar_token_openrouter():
    """Verifica el token de OpenRouter haciendo una llamada de prueba."""
    print("=" * 70)
    print("DIAGNÓSTICO DE ERROR 401 - USER NOT FOUND")
    print("=" * 70)
    print()
    
    # Obtener credenciales
    api_key = AIConfigService.obtener_api_key()
    model = AIConfigService.obtener_modelo()
    base_url = AIConfigService.obtener_base_url()
    
    print("📋 CONFIGURACIÓN ACTUAL:")
    print("-" * 70)
    print(f"API Key: {api_key[:20]}...{api_key[-10:] if api_key else 'No configurada'}")
    print(f"Modelo: {model}")
    print(f"Base URL: {base_url}")
    print()
    
    if not api_key:
        print("❌ ERROR: No hay API key configurada")
        return
    
    if not api_key.startswith('sk-or-v1-'):
        print("⚠️  ADVERTENCIA: El token no parece ser de OpenRouter")
        print(f"   Formato esperado: sk-or-v1-...")
        print(f"   Formato actual: {api_key[:10]}...")
        print()
    
    # Preparar headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if 'openrouter.ai' in base_url.lower():
        if Config.OPENROUTER_HTTP_REFERER:
            headers["HTTP-Referer"] = Config.OPENROUTER_HTTP_REFERER
            print(f"✅ HTTP-Referer agregado: {Config.OPENROUTER_HTTP_REFERER}")
        else:
            print("⚠️  HTTP-Referer NO configurado")
        
        if Config.OPENROUTER_X_TITLE:
            headers["X-Title"] = Config.OPENROUTER_X_TITLE
            print(f"✅ X-Title agregado: {Config.OPENROUTER_X_TITLE}")
        else:
            print("⚠️  X-Title NO configurado")
    
    print()
    print("=" * 70)
    print("PRUEBA 1: Verificar endpoint /models")
    print("=" * 70)
    print()
    
    try:
        # Probar endpoint /models (más simple, no requiere créditos)
        response = requests.get(
            f"{base_url}/models",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print()
        
        if response.status_code == 200:
            print("✅ Endpoint /models funciona correctamente")
            print("   El token es válido para consultar modelos")
        elif response.status_code == 401:
            print("❌ Error 401 en /models")
            print("   El token NO es válido o ha expirado")
            print()
            print("POSIBLES CAUSAS:")
            print("1. El token es inválido o ha sido revocado")
            print("2. El token pertenece a otra cuenta")
            print("3. El token no tiene permisos suficientes")
        else:
            print(f"⚠️  Status code inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Error al llamar a /models: {str(e)}")
    
    print()
    print("=" * 70)
    print("PRUEBA 2: Verificar endpoint /chat/completions")
    print("=" * 70)
    print()
    
    try:
        # Probar endpoint /chat/completions (el que usa el chat)
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hola"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        print()
        
        if response.status_code == 200:
            print("✅ Endpoint /chat/completions funciona correctamente")
            result = response.json()
            print(f"   Respuesta del AI: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        elif response.status_code == 401:
            print("❌ Error 401 en /chat/completions")
            print("   Mensaje: User not found")
            print()
            print("POSIBLES CAUSAS:")
            print("1. El token no tiene créditos en OpenRouter")
            print("2. El token está asociado a una cuenta diferente")
            print("3. El token ha sido revocado o desactivado")
            print("4. La cuenta de OpenRouter tiene problemas")
            print()
            print("SOLUCIONES:")
            print("1. Verifica tu cuenta en https://openrouter.ai/")
            print("2. Verifica que tengas créditos disponibles")
            print("3. Genera un nuevo token si es necesario")
            print("4. Verifica que el token sea correcto")
        elif response.status_code == 402:
            print("❌ Error 402: Payment Required")
            print("   No tienes créditos suficientes en OpenRouter")
            print()
            print("SOLUCIÓN: Agrega créditos a tu cuenta en https://openrouter.ai/")
        else:
            print(f"⚠️  Status code inesperado: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error al llamar a /chat/completions: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("RECOMENDACIONES")
    print("=" * 70)
    print()
    
    print("Si el error 401 persiste:")
    print()
    print("1. Verifica tu cuenta de OpenRouter:")
    print("   - Ve a https://openrouter.ai/")
    print("   - Inicia sesión con tu cuenta")
    print("   - Verifica que el token pertenezca a tu cuenta")
    print()
    print("2. Verifica créditos:")
    print("   - Ve a tu dashboard de OpenRouter")
    print("   - Verifica que tengas créditos disponibles")
    print("   - El error 401 puede aparecer si no hay créditos")
    print()
    print("3. Genera un nuevo token:")
    print("   - Ve a https://openrouter.ai/keys")
    print("   - Crea un nuevo token")
    print("   - Actualiza OPENROUTER_API_KEY en Render.com")
    print()
    print("4. Verifica el formato del token:")
    print("   - Debe comenzar con: sk-or-v1-")
    print("   - Debe tener al menos 50 caracteres")
    print()
    print("=" * 70)

if __name__ == '__main__':
    verificar_token_openrouter()
