"""
Script para configurar OpenRouter rápidamente.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from modules.configuracion.ai import AIConfigService

# Token de OpenRouter proporcionado
OPENROUTER_TOKEN = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"  # Puedes cambiar esto según tus necesidades

def configurar_openrouter():
    """Configura OpenRouter en el sistema."""
    print("=" * 60)
    print("CONFIGURACIÓN DE OPENROUTER")
    print("=" * 60)
    
    print(f"\n🔑 Token: {OPENROUTER_TOKEN[:20]}...{OPENROUTER_TOKEN[-10:]}")
    print(f"🌐 Base URL: {OPENROUTER_BASE_URL}")
    print(f"🤖 Modelo: {OPENROUTER_MODEL}")
    
    # Actualizar token en memoria
    resultado = AIConfigService.actualizar_token(
        api_key=OPENROUTER_TOKEN,
        modelo=OPENROUTER_MODEL,
        base_url=OPENROUTER_BASE_URL
    )
    
    if resultado.get('exito'):
        print("\n✅ Token configurado correctamente en memoria")
        print(f"   {resultado.get('mensaje')}")
        print(f"   ⚠️  {resultado.get('nota')}")
        
        # Verificar configuración
        print("\n🔍 Verificando configuración...")
        config = AIConfigService.obtener_configuracion()
        print(f"   Estado: {config.get('estado')}")
        print(f"   Proveedor: {config.get('proveedor', 'N/A')}")
        print(f"   Modelo: {config.get('openai_model')}")
        print(f"   Base URL: {config.get('openai_base_url')}")
        
        # Verificar que funciona
        print("\n🧪 Verificando conexión con OpenRouter...")
        verificacion = AIConfigService.verificar_configuracion()
        
        if verificacion.get('valido'):
            print(f"   ✅ {verificacion.get('mensaje')}")
            print(f"   📝 {verificacion.get('detalles')}")
        else:
            print(f"   ⚠️  {verificacion.get('mensaje')}")
            print(f"   📝 {verificacion.get('detalles')}")
        
        # Enviar mensaje de prueba
        print("\n💬 Enviando mensaje de prueba...")
        prueba = AIConfigService.enviar_mensaje_prueba("Responde solo con 'OK'")
        
        if prueba.get('exito'):
            print(f"   ✅ Respuesta: {prueba.get('respuesta')}")
            print(f"   📊 Tokens usados: {prueba.get('tokens_usados', 0)}")
        else:
            print(f"   ⚠️  Error: {prueba.get('error')}")
        
    else:
        print(f"\n❌ Error: {resultado.get('error')}")
        return False
    
    print("\n" + "=" * 60)
    print("📋 PRÓXIMOS PASOS")
    print("=" * 60)
    print("\n1. Para hacer la configuración permanente, agrega estas variables a tu .env:")
    print(f"   OPENROUTER_API_KEY={OPENROUTER_TOKEN}")
    print(f"   OPENAI_BASE_URL={OPENROUTER_BASE_URL}")
    print(f"   OPENAI_MODEL={OPENROUTER_MODEL}")
    print("\n2. Puedes cambiar el modelo según tus necesidades:")
    print("   - openai/gpt-3.5-turbo (económico)")
    print("   - openai/gpt-4o (más potente)")
    print("   - anthropic/claude-3.5-sonnet (muy potente)")
    print("\n3. Ver más modelos en: https://openrouter.ai/models")
    print("\n" + "=" * 60)
    
    return True

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        configurar_openrouter()
