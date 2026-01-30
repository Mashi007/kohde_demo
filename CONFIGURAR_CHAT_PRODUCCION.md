# Configuración del Chat AI en Producción (Render.com)

## Problema

Si el chat muestra el error: "No se ha configurado la API key", significa que las variables de entorno no están configuradas en Render.com.

## Solución

### Paso 1: Configurar Variables de Entorno en Render.com

1. Ve a tu servicio en [Render Dashboard](https://dashboard.render.com)
2. Selecciona tu servicio (backend)
3. Ve a la sección **"Environment"** en el menú lateral
4. Agrega las siguientes variables de entorno:

#### Para OpenRouter (Recomendado):

```
OPENROUTER_API_KEY=sk-or-v1-tu-token-aqui
OPENAI_MODEL=openai/gpt-3.5-turbo
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://github.com/Mashi007/kohde_demo.git
OPENROUTER_X_TITLE=Kohde ERP Restaurantes
```

#### O para OpenAI directamente:

```
OPENAI_API_KEY=sk-tu-token-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Paso 2: Reiniciar el Servicio

Después de agregar las variables de entorno:

1. Ve a la sección **"Manual Deploy"** o **"Events"**
2. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**
3. O simplemente espera a que Render detecte los cambios y despliegue automáticamente

### Paso 3: Verificar la Configuración

Una vez desplegado, puedes verificar que todo esté funcionando:

1. Ve a `/chat` en tu aplicación
2. Envía un mensaje de prueba como "hola"
3. Deberías recibir una respuesta del AI

## Verificación Local

Si quieres verificar la configuración localmente antes de desplegar:

```bash
python scripts/diagnostico_chat.py
```

Este script mostrará:
- ✅ Qué variables de entorno están configuradas
- ✅ Qué credenciales está usando el servicio
- ✅ Si hay algún problema de configuración

## Notas Importantes

1. **Prioridad de API Keys**: El sistema usa esta prioridad:
   - Token en memoria (si se configuró desde la UI)
   - `OPENROUTER_API_KEY`
   - `OPENAI_API_KEY`

2. **OpenRouter vs OpenAI**: 
   - OpenRouter requiere headers adicionales (`HTTP-Referer`, `X-Title`)
   - Estos headers se agregan automáticamente si `OPENROUTER_HTTP_REFERER` está configurado

3. **Seguridad**: 
   - Nunca compartas tus API keys
   - Las variables de entorno en Render son privadas y seguras
   - No las incluyas en el código fuente

## Solución de Problemas

### Error: "No se ha configurado la API key"

**Causa**: Las variables de entorno no están configuradas o el servicio no se ha reiniciado.

**Solución**:
1. Verifica que las variables estén en Render.com → Environment
2. Reinicia el servicio manualmente
3. Espera 1-2 minutos para que los cambios surtan efecto

### Error: "Error al llamar a la API: 401"

**Causa**: El token es inválido o no tiene créditos.

**Solución**:
1. Verifica que el token sea correcto
2. Si usas OpenRouter, verifica que tengas créditos en tu cuenta
3. Si usas OpenAI, verifica que el token tenga permisos para Chat Completions

### El chat no responde o tarda mucho

**Causa**: Timeout o problemas de conectividad.

**Solución**:
1. Verifica tu conexión a internet
2. Verifica que la API de OpenRouter/OpenAI esté disponible
3. Revisa los logs de Render para ver errores específicos

## Contacto

Si después de seguir estos pasos el problema persiste, revisa los logs de Render para más detalles del error.
