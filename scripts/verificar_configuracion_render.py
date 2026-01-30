"""
Script para verificar que la configuración en Render.com esté correcta.
Compara las variables esperadas con las que deberían estar configuradas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config

def main():
    """Verifica la configuración esperada vs actual."""
    print("=" * 70)
    print("VERIFICACIÓN DE CONFIGURACIÓN EN RENDER.COM")
    print("=" * 70)
    print()
    
    print("📋 VARIABLES ESPERADAS (según captura de pantalla):")
    print("-" * 70)
    
    # Variables que vimos en la captura
    # ⚠️ IMPORTANTE: NO hardcodees tokens aquí. Solo valores de referencia para comparación.
    variables_esperadas = {
        'OPENROUTER_API_KEY': None,  # Se compara con Config.OPENROUTER_API_KEY (de variables de entorno)
        'OPENAI_MODEL': 'openai/gpt-3.5-turbo',
        'OPENROUTER_HTTP_REFERER': 'https://github.com/Mashi007/kohde_demo.git',
        'OPENROUTER_X_TITLE': 'Kohde ERP Restaurantes',
        'OPENAI_BASE_URL': 'https://openrouter.ai/api/v1',  # Debería estar configurada aunque esté oculta
    }
    
    print("Variables que DEBEN estar configuradas en Render.com:")
    print()
    for var_name, var_value_esperado in variables_esperadas.items():
        var_value_actual = getattr(Config, var_name, None)
        
        if var_name == 'OPENROUTER_API_KEY':
            # Verificar solo que esté configurada, sin comparar valores específicos
            if var_value_actual:
                if var_value_actual.startswith('sk-or-v1-'):
                    print(f"✅ {var_name}: Configurada correctamente (OpenRouter)")
                    print(f"   Valor (últimos 10 chars): ...{var_value_actual[-10:]}")
                elif var_value_actual.startswith('sk-'):
                    print(f"⚠️  {var_name}: Configurada pero parece ser de OpenAI (esperado OpenRouter)")
                    print(f"   Valor (últimos 10 chars): ...{var_value_actual[-10:]}")
                else:
                    print(f"⚠️  {var_name}: Configurada pero formato inesperado")
                    print(f"   Valor (últimos 10 chars): ...{var_value_actual[-10:]}")
            else:
                print(f"❌ {var_name}: NO configurada")
                print(f"   Debe comenzar con: sk-or-v1-...")
        else:
            if var_value_actual == var_value_esperado:
                print(f"✅ {var_name}: {var_value_actual}")
            elif var_value_actual:
                print(f"⚠️  {var_name}: Valor diferente")
                print(f"   Esperado: {var_value_esperado}")
                print(f"   Actual: {var_value_actual}")
            else:
                print(f"❌ {var_name}: NO configurada")
                print(f"   Esperado: {var_value_esperado}")
    
    print()
    print("=" * 70)
    print("VERIFICACIÓN DE USO EN EL CÓDIGO")
    print("=" * 70)
    print()
    
    # Verificar cómo se usan en el código
    from modules.configuracion.ai import AIConfigService
    
    api_key = AIConfigService.obtener_api_key()
    model = AIConfigService.obtener_modelo()
    base_url = AIConfigService.obtener_base_url()
    
    print("Valores que el código está usando:")
    print()
    
    if api_key:
        if api_key.startswith('sk-or-v1-'):
            print(f"✅ API Key: OpenRouter (tipo correcto)")
            print(f"   Últimos 10 chars: ...{api_key[-10:]}")
        else:
            print(f"⚠️  API Key: Tipo diferente (esperado OpenRouter)")
    else:
        print(f"❌ API Key: No disponible")
    
    print(f"{'✅' if model == 'openai/gpt-3.5-turbo' else '⚠️ '} Modelo: {model}")
    print(f"{'✅' if 'openrouter.ai' in base_url.lower() else '⚠️ '} Base URL: {base_url}")
    
    print()
    print("=" * 70)
    print("RECOMENDACIONES")
    print("=" * 70)
    print()
    
    # Verificar OPENAI_BASE_URL
    if not Config.OPENAI_BASE_URL or Config.OPENAI_BASE_URL == '':
        print("⚠️  IMPORTANTE: OPENAI_BASE_URL no está configurada")
        print("   Debe ser: https://openrouter.ai/api/v1")
        print("   Agrégalo en Render.com → Environment")
    else:
        if 'openrouter.ai' in Config.OPENAI_BASE_URL.lower():
            print("✅ OPENAI_BASE_URL está configurada correctamente")
        else:
            print(f"⚠️  OPENAI_BASE_URL tiene un valor diferente: {Config.OPENAI_BASE_URL}")
            print("   Debería ser: https://openrouter.ai/api/v1")
    
    print()
    
    # Verificar que todo esté listo
    if api_key and model and base_url:
        print("✅ CONFIGURACIÓN COMPLETA")
        print()
        print("El chat debería funcionar correctamente con esta configuración.")
        print("Para probar:")
        print("1. Ve a https://kohde-demo-1.onrender.com/chat")
        print("2. Envía un mensaje de prueba")
        print("3. Deberías recibir una respuesta del AI")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print()
        print("Faltan algunas variables. Revisa la lista anterior.")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()
