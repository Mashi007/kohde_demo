"""
Script para verificar la configuración de OpenRouter.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from modules.configuracion.ai import AIConfigService

def verificar_configuracion():
    """Verifica la configuración completa de OpenRouter."""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN OPENROUTER")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    print("\n1️⃣ Verificando variables de entorno (.env)...")
    print(f"   OPENROUTER_API_KEY: {'✅ Configurado' if Config.OPENROUTER_API_KEY else '❌ No configurado'}")
    if Config.OPENROUTER_API_KEY:
        preview = Config.OPENROUTER_API_KEY[:20] + '...' + Config.OPENROUTER_API_KEY[-10:]
        print(f"      Token: {preview}")
    
    print(f"   OPENAI_BASE_URL: {Config.OPENAI_BASE_URL}")
    print(f"   OPENAI_MODEL: {Config.OPENAI_MODEL}")
    print(f"   OPENROUTER_HTTP_REFERER: {Config.OPENROUTER_HTTP_REFERER or 'No configurado'}")
    print(f"   OPENROUTER_X_TITLE: {Config.OPENROUTER_X_TITLE or 'No configurado'}")
    
    # 2. Verificar configuración del servicio
    print("\n2️⃣ Verificando configuración del servicio AI...")
    config = AIConfigService.obtener_configuracion()
    print(f"   Estado: {config.get('estado', 'N/A')}")
    print(f"   Proveedor: {config.get('proveedor', 'N/A')}")
    print(f"   Es OpenRouter: {config.get('es_openrouter', False)}")
    print(f"   Modelo: {config.get('openai_model', 'N/A')}")
    print(f"   Base URL: {config.get('openai_base_url', 'N/A')}")
    print(f"   Token en memoria: {'Sí' if config.get('token_en_memoria') else 'No'}")
    
    # 3. Verificar conexión
    print("\n3️⃣ Verificando conexión con OpenRouter...")
    verificacion = AIConfigService.verificar_configuracion()
    
    if verificacion.get('valido'):
        print(f"   ✅ {verificacion.get('mensaje')}")
        print(f"   📝 {verificacion.get('detalles')}")
    else:
        print(f"   ❌ {verificacion.get('mensaje')}")
        print(f"   📝 {verificacion.get('detalles')}")
        return False
    
    # 4. Prueba de mensaje
    print("\n4️⃣ Enviando mensaje de prueba...")
    prueba = AIConfigService.enviar_mensaje_prueba("Responde solo con 'OK'")
    
    if prueba.get('exito'):
        print(f"   ✅ Respuesta recibida: {prueba.get('respuesta')}")
        print(f"   📊 Tokens usados: {prueba.get('tokens_usados', 0)}")
    else:
        print(f"   ⚠️  Error: {prueba.get('error')}")
        return False
    
    # 5. Resumen final
    print("\n" + "=" * 60)
    print("✅ RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    print("\n✅ Variables de entorno: Configuradas correctamente")
    print("✅ Token de OpenRouter: Válido y funcionando")
    print("✅ Conexión con OpenRouter: Operativa")
    print("✅ Modelo configurado: " + Config.OPENAI_MODEL)
    print("\n🎉 La configuración de OpenRouter está completa y funcionando!")
    print("\n💡 Nota: Si cambias variables en el .env, reinicia el servidor Flask")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        verificar_configuracion()
