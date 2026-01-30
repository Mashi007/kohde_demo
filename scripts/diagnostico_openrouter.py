"""
Script de diagnóstico detallado para OpenRouter.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
import requests

def diagnostico_completo():
    """Realiza un diagnóstico completo de la configuración de OpenRouter."""
    print("=" * 60)
    print("DIAGNÓSTICO COMPLETO DE OPENROUTER")
    print("=" * 60)
    
    api_key = Config.OPENROUTER_API_KEY or Config.OPENAI_API_KEY
    base_url = Config.OPENAI_BASE_URL
    modelo = Config.OPENAI_MODEL
    
    print(f"\n🔑 Token: {api_key[:25]}...{api_key[-10:] if api_key else 'N/A'}")
    print(f"🌐 Base URL: {base_url}")
    print(f"🤖 Modelo: {modelo}")
    
    if not api_key:
        print("\n❌ ERROR: No hay token configurado")
        return
    
    # Test 1: Verificar endpoint de modelos
    print("\n" + "=" * 60)
    print("TEST 1: Verificar endpoint /models")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if 'openrouter.ai' in base_url:
        headers["HTTP-Referer"] = Config.OPENROUTER_HTTP_REFERER or "https://github.com/Mashi007/kohde_demo"
        if Config.OPENROUTER_X_TITLE:
            headers["X-Title"] = Config.OPENROUTER_X_TITLE
    
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint /models funciona correctamente")
            models_data = response.json()
            if 'data' in models_data:
                print(f"   📊 Modelos disponibles: {len(models_data['data'])}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Excepción: {str(e)}")
    
    # Test 2: Verificar endpoint de chat/completions
    print("\n" + "=" * 60)
    print("TEST 2: Verificar endpoint /chat/completions")
    print("=" * 60)
    
    chat_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if 'openrouter.ai' in base_url:
        # HTTP-Referer es CRÍTICO para OpenRouter
        referer = Config.OPENROUTER_HTTP_REFERER or "https://github.com/Mashi007/kohde_demo"
        chat_headers["HTTP-Referer"] = referer
        print(f"   📝 HTTP-Referer: {referer}")
        if Config.OPENROUTER_X_TITLE:
            chat_headers["X-Title"] = Config.OPENROUTER_X_TITLE
            print(f"   📝 X-Title: {Config.OPENROUTER_X_TITLE}")
    
    data = {
        "model": modelo,
        "messages": [
            {"role": "user", "content": "Responde solo con OK"}
        ],
        "max_tokens": 10
    }
    
    print(f"   📤 Enviando petición a: {base_url}/chat/completions")
    print(f"   📤 Modelo: {modelo}")
    print(f"   📤 Headers: {list(chat_headers.keys())}")
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=chat_headers,
            json=data,
            timeout=30
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Chat funciona correctamente")
            if 'choices' in result and len(result['choices']) > 0:
                respuesta = result['choices'][0]['message']['content']
                print(f"   💬 Respuesta: {respuesta}")
                if 'usage' in result:
                    print(f"   📊 Tokens: {result['usage'].get('total_tokens', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
            try:
                error_json = response.json()
                print(f"   📝 Detalles: {error_json}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ Excepción: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Verificar formato del token
    print("\n" + "=" * 60)
    print("TEST 3: Verificar formato del token")
    print("=" * 60)
    
    if api_key.startswith('sk-or-v1-'):
        print("   ✅ Formato correcto: Token de OpenRouter (sk-or-v1-...)")
    elif api_key.startswith('sk-'):
        print("   ✅ Formato correcto: Token de OpenAI (sk-...)")
    else:
        print(f"   ⚠️  Formato inusual: {api_key[:20]}...")
    
    print(f"   📏 Longitud: {len(api_key)} caracteres")
    
    print("\n" + "=" * 60)
    print("RECOMENDACIONES")
    print("=" * 60)
    
    if 'openrouter.ai' in base_url:
        print("\n✅ Para OpenRouter, asegúrate de:")
        print("   1. El token empiece con 'sk-or-v1-'")
        print("   2. HTTP-Referer esté configurado (requerido)")
        print("   3. El token tenga créditos disponibles")
        print("   4. Verifica tu cuenta en: https://openrouter.ai/keys")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        diagnostico_completo()
