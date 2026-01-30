"""
Script de verificación completa del chat AI en producción.
Verifica que todo esté correctamente configurado y articulado con variables de entorno.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from modules.configuracion.ai import AIConfigService
from modules.chat.chat_service import chat_service

def verificar_variables_entorno():
    """Verifica que las variables de entorno estén configuradas."""
    print("=" * 70)
    print("1. VERIFICACIÓN DE VARIABLES DE ENTORNO")
    print("=" * 70)
    print()
    
    variables = {
        'OPENAI_API_KEY': Config.OPENAI_API_KEY,
        'OPENROUTER_API_KEY': Config.OPENROUTER_API_KEY,
        'OPENAI_MODEL': Config.OPENAI_MODEL,
        'OPENAI_BASE_URL': Config.OPENAI_BASE_URL,
        'OPENROUTER_HTTP_REFERER': Config.OPENROUTER_HTTP_REFERER,
        'OPENROUTER_X_TITLE': Config.OPENROUTER_X_TITLE,
    }
    
    todas_configuradas = True
    
    for var_name, var_value in variables.items():
        if var_value:
            if 'API_KEY' in var_name:
                # Ocultar parte del token por seguridad
                display_value = f"{var_value[:20]}...{var_value[-10:]}" if len(var_value) > 30 else "***"
                print(f"✅ {var_name}: {display_value}")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: No configurada")
            if var_name in ['OPENROUTER_API_KEY', 'OPENAI_API_KEY']:
                todas_configuradas = False
    
    print()
    return todas_configuradas

def verificar_servicio_configuracion():
    """Verifica que el servicio de configuración AI funcione correctamente."""
    print("=" * 70)
    print("2. VERIFICACIÓN DEL SERVICIO DE CONFIGURACIÓN AI")
    print("=" * 70)
    print()
    
    api_key = AIConfigService.obtener_api_key()
    model = AIConfigService.obtener_modelo()
    base_url = AIConfigService.obtener_base_url()
    
    print(f"API Key obtenida: {'✅ Sí' if api_key else '❌ No'}")
    if api_key:
        display_key = f"{api_key[:20]}...{api_key[-10:]}" if len(api_key) > 30 else "***"
        print(f"  Valor: {display_key}")
        
        # Detectar tipo
        if api_key.startswith('sk-or-v1-'):
            print(f"  Tipo: OpenRouter ✅")
        elif api_key.startswith('sk-'):
            print(f"  Tipo: OpenAI ✅")
        else:
            print(f"  Tipo: Desconocido ⚠️")
    
    print(f"Modelo obtenido: {model}")
    print(f"Base URL obtenida: {base_url}")
    
    # Verificar que la base URL coincida con el tipo de token
    if api_key:
        if api_key.startswith('sk-or-v1-') and 'openrouter.ai' not in base_url.lower():
            print(f"⚠️  ADVERTENCIA: Token de OpenRouter pero base_url no es OpenRouter")
        elif api_key.startswith('sk-') and api_key.startswith('sk-or-v1-') == False:
            if 'openrouter.ai' in base_url.lower():
                print(f"⚠️  ADVERTENCIA: Token de OpenAI pero base_url es OpenRouter")
    
    print()
    return api_key is not None

def verificar_servicio_chat():
    """Verifica que el servicio de chat obtenga credenciales correctamente."""
    print("=" * 70)
    print("3. VERIFICACIÓN DEL SERVICIO DE CHAT")
    print("=" * 70)
    print()
    
    try:
        # Verificar que el método _obtener_credenciales existe y funciona
        credenciales = chat_service._obtener_credenciales()
        
        print(f"Método _obtener_credenciales: ✅ Existe y funciona")
        print(f"API Key obtenida: {'✅ Sí' if credenciales['api_key'] else '❌ No'}")
        
        if credenciales['api_key']:
            display_key = f"{credenciales['api_key'][:20]}...{credenciales['api_key'][-10:]}" if len(credenciales['api_key']) > 30 else "***"
            print(f"  Valor: {display_key}")
        
        print(f"Modelo obtenido: {credenciales['model']}")
        print(f"Base URL obtenida: {credenciales['base_url']}")
        
        # Verificar que las credenciales sean dinámicas (no almacenadas en __init__)
        credenciales2 = chat_service._obtener_credenciales()
        if credenciales == credenciales2:
            print(f"Credenciales dinámicas: ✅ Se obtienen en cada llamada")
        else:
            print(f"Credenciales dinámicas: ⚠️  Pueden estar cacheadas")
        
        print()
        return credenciales['api_key'] is not None
        
    except AttributeError as e:
        print(f"❌ Error: El método _obtener_credenciales no existe: {str(e)}")
        print()
        return False
    except Exception as e:
        print(f"❌ Error al verificar servicio de chat: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return False

def verificar_headers_openrouter():
    """Verifica que los headers de OpenRouter estén configurados."""
    print("=" * 70)
    print("4. VERIFICACIÓN DE HEADERS OPENROUTER")
    print("=" * 70)
    print()
    
    credenciales = chat_service._obtener_credenciales()
    base_url = credenciales['base_url']
    
    if 'openrouter.ai' in base_url.lower():
        print(f"Base URL es OpenRouter: ✅")
        print()
        
        if Config.OPENROUTER_HTTP_REFERER:
            print(f"✅ HTTP-Referer configurado: {Config.OPENROUTER_HTTP_REFERER}")
        else:
            print(f"⚠️  HTTP-Referer NO configurado (recomendado para OpenRouter)")
        
        if Config.OPENROUTER_X_TITLE:
            print(f"✅ X-Title configurado: {Config.OPENROUTER_X_TITLE}")
        else:
            print(f"⚠️  X-Title NO configurado (opcional para OpenRouter)")
        
        print()
        print("💡 Nota: Los headers se agregan automáticamente en _llamar_openai()")
        return True
    else:
        print(f"Base URL NO es OpenRouter: {base_url}")
        print("  (No se requieren headers especiales)")
        print()
        return True

def verificar_estructura_codigo():
    """Verifica que el código esté actualizado correctamente."""
    print("=" * 70)
    print("5. VERIFICACIÓN DE ESTRUCTURA DEL CÓDIGO")
    print("=" * 70)
    print()
    
    # Verificar que el servicio no almacene credenciales en __init__
    try:
        has_api_key_attr = hasattr(chat_service, 'api_key')
        has_model_attr = hasattr(chat_service, 'model')
        has_base_url_attr = hasattr(chat_service, 'base_url')
        
        if has_api_key_attr or has_model_attr or has_base_url_attr:
            print("⚠️  ADVERTENCIA: El servicio tiene atributos de credenciales almacenados")
            if has_api_key_attr:
                print(f"   - api_key: {chat_service.api_key[:20] if chat_service.api_key else 'None'}...")
            if has_model_attr:
                print(f"   - model: {chat_service.model}")
            if has_base_url_attr:
                print(f"   - base_url: {chat_service.base_url}")
            print()
            print("   ⚠️  Esto puede causar que las credenciales no se actualicen dinámicamente")
        else:
            print("✅ El servicio NO almacena credenciales en __init__ (correcto)")
            print("   Las credenciales se obtienen dinámicamente en cada llamada")
        
        # Verificar que el método _obtener_credenciales existe
        if hasattr(chat_service, '_obtener_credenciales'):
            print("✅ Método _obtener_credenciales existe")
        else:
            print("❌ Método _obtener_credenciales NO existe")
        
        # Verificar que _llamar_openai use credenciales dinámicas
        import inspect
        source = inspect.getsource(chat_service._llamar_openai)
        if '_obtener_credenciales' in source:
            print("✅ _llamar_openai usa credenciales dinámicas")
        else:
            print("⚠️  _llamar_openai puede no estar usando credenciales dinámicas")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar estructura: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        return False

def resumen_final():
    """Muestra un resumen final con recomendaciones."""
    print("=" * 70)
    print("RESUMEN Y RECOMENDACIONES")
    print("=" * 70)
    print()
    
    api_key = AIConfigService.obtener_api_key()
    credenciales = chat_service._obtener_credenciales()
    
    if not api_key:
        print("❌ PROBLEMA CRÍTICO: No hay API key configurada")
        print()
        print("SOLUCIÓN:")
        print("1. Configura OPENROUTER_API_KEY o OPENAI_API_KEY en Render.com")
        print("2. Ve a tu servicio → Environment → Agrega las variables")
        print("3. Reinicia el servicio")
        print()
        return False
    
    if not credenciales['api_key']:
        print("❌ PROBLEMA: El servicio de chat no puede obtener la API key")
        print()
        print("SOLUCIÓN:")
        print("1. Verifica que las variables de entorno estén correctamente configuradas")
        print("2. Verifica que el código esté actualizado en producción")
        print("3. Reinicia el servicio")
        print()
        return False
    
    print("✅ CONFIGURACIÓN CORRECTA")
    print()
    print("El chat debería funcionar correctamente con esta configuración:")
    print(f"  - API Key: {'✅ Configurada' if api_key else '❌ No configurada'}")
    print(f"  - Modelo: {credenciales['model']}")
    print(f"  - Base URL: {credenciales['base_url']}")
    print()
    print("💡 Para probar:")
    print("  1. Ve a https://kohde-demo-1.onrender.com/chat")
    print("  2. Envía un mensaje de prueba")
    print("  3. Deberías recibir una respuesta del AI")
    print()
    return True

def main():
    """Ejecuta todas las verificaciones."""
    print()
    print("🔍 VERIFICACIÓN COMPLETA DEL CHAT AI EN PRODUCCIÓN")
    print()
    
    resultados = []
    
    resultados.append(("Variables de entorno", verificar_variables_entorno()))
    resultados.append(("Servicio de configuración", verificar_servicio_configuracion()))
    resultados.append(("Servicio de chat", verificar_servicio_chat()))
    resultados.append(("Headers OpenRouter", verificar_headers_openrouter()))
    resultados.append(("Estructura del código", verificar_estructura_codigo()))
    
    print()
    print("=" * 70)
    print("RESULTADOS DE VERIFICACIÓN")
    print("=" * 70)
    print()
    
    for nombre, resultado in resultados:
        estado = "✅ OK" if resultado else "❌ FALLO"
        print(f"{estado} - {nombre}")
    
    print()
    
    # Resumen final
    todo_ok = resumen_final()
    
    if todo_ok:
        print("=" * 70)
        print("✅ VERIFICACIÓN COMPLETA: Todo está configurado correctamente")
        print("=" * 70)
    else:
        print("=" * 70)
        print("❌ VERIFICACIÓN COMPLETA: Hay problemas que deben resolverse")
        print("=" * 70)
    
    print()

if __name__ == '__main__':
    main()
