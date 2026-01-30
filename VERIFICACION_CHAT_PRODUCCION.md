# Verificación del Chat AI en Producción

## Estado Actual del Código

✅ **El código está correctamente actualizado y articulado con variables de entorno:**

### 1. Obtención Dinámica de Credenciales
- ✅ El servicio `ChatService` NO almacena credenciales en `__init__`
- ✅ Las credenciales se obtienen dinámicamente en cada llamada mediante `_obtener_credenciales()`
- ✅ Esto permite que los cambios en variables de entorno se reflejen sin reiniciar

### 2. Integración con Variables de Entorno
- ✅ Usa `AIConfigService` que prioriza:
  1. Token en memoria (si se configuró desde UI)
  2. `OPENROUTER_API_KEY`
  3. `OPENAI_API_KEY`
- ✅ Obtiene modelo desde `OPENAI_MODEL` (default: `openai/gpt-3.5-turbo`)
- ✅ Obtiene base URL desde `OPENAI_BASE_URL` (default: `https://openrouter.ai/api/v1`)

### 3. Headers de OpenRouter
- ✅ Detecta automáticamente si es OpenRouter por la base URL
- ✅ Agrega `HTTP-Referer` desde `OPENROUTER_HTTP_REFERER`
- ✅ Agrega `X-Title` desde `OPENROUTER_X_TITLE`

### 4. Manejo de Errores
- ✅ Mensajes de error claros cuando no hay API key
- ✅ Manejo de errores de conexión y API
- ✅ Logging para debugging

## Variables de Entorno Requeridas en Render.com

Para que el chat funcione correctamente, configura estas variables en Render.com:

### Opción 1: OpenRouter (Recomendado)
```
OPENROUTER_API_KEY=sk-or-v1-tu-token-aqui
OPENAI_MODEL=openai/gpt-3.5-turbo
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_HTTP_REFERER=https://github.com/Mashi007/kohde_demo.git
OPENROUTER_X_TITLE=Kohde ERP Restaurantes
```

### Opción 2: OpenAI Directo
```
OPENAI_API_KEY=sk-tu-token-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

## Cómo Verificar que Está Funcionando

### 1. Verificación Local (Antes de Desplegar)

Ejecuta el script de verificación:

```bash
python scripts/verificar_chat_produccion.py
```

Este script verifica:
- ✅ Variables de entorno configuradas
- ✅ Servicio de configuración AI funcionando
- ✅ Servicio de chat obteniendo credenciales correctamente
- ✅ Headers de OpenRouter configurados
- ✅ Estructura del código correcta

### 2. Verificación en Producción

#### Paso 1: Verificar Variables de Entorno en Render
1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Selecciona tu servicio
3. Ve a **Environment**
4. Verifica que todas las variables estén configuradas

#### Paso 2: Verificar que el Código Esté Actualizado
1. Verifica que el último commit esté desplegado
2. Revisa los logs de Render para ver si hay errores
3. Busca en los logs: "Error: No se ha configurado la API key"

#### Paso 3: Probar el Chat
1. Ve a `https://kohde-demo-1.onrender.com/chat`
2. Envía un mensaje de prueba: "hola"
3. Deberías recibir una respuesta del AI

## Flujo de Obtención de Credenciales

```
Usuario envía mensaje
    ↓
ChatService.enviar_mensaje()
    ↓
ChatService._llamar_openai()
    ↓
ChatService._obtener_credenciales()
    ↓
AIConfigService.obtener_api_key()
    ↓
Prioridad:
  1. Token en memoria (_token_en_memoria)
  2. Config.OPENROUTER_API_KEY
  3. Config.OPENAI_API_KEY
    ↓
Usa credenciales para llamar a la API
```

## Características del Sistema

### ✅ Ventajas del Sistema Actual

1. **Dinámico**: Las credenciales se obtienen en cada llamada
2. **Flexible**: Soporta OpenRouter y OpenAI
3. **Priorización**: Usa token en memoria si está disponible (configuración desde UI)
4. **Seguro**: No almacena credenciales en memoria permanente
5. **Robusto**: Manejo de errores completo

### 🔧 Configuración desde UI

El sistema también permite configurar el token desde la interfaz de usuario:
- Ve a `/configuracion/ai`
- Ingresa el token
- Se guarda en memoria (temporal, hasta reiniciar)
- Tiene prioridad sobre variables de entorno

## Solución de Problemas

### Problema: "No se ha configurado la API key"

**Causa**: Las variables de entorno no están configuradas o el servicio no se ha reiniciado.

**Solución**:
1. Verifica que las variables estén en Render.com → Environment
2. Reinicia el servicio manualmente
3. Espera 1-2 minutos

### Problema: El chat no responde

**Causa**: Token inválido o sin créditos.

**Solución**:
1. Verifica que el token sea correcto
2. Si usas OpenRouter, verifica créditos en tu cuenta
3. Revisa los logs de Render para ver el error específico

### Problema: Las variables no se actualizan

**Causa**: El código antiguo almacenaba credenciales en `__init__`.

**Solución**:
- ✅ Ya está corregido: el código actual obtiene credenciales dinámicamente
- Si aún tienes problemas, verifica que el código esté actualizado en producción

## Archivos Clave

- `modules/chat/chat_service.py`: Servicio principal del chat
- `modules/configuracion/ai.py`: Servicio de configuración AI
- `config.py`: Configuración de variables de entorno
- `routes/chat_routes.py`: Rutas API del chat
- `scripts/verificar_chat_produccion.py`: Script de verificación

## Próximos Pasos

1. ✅ Código actualizado y verificado
2. ⏳ Configurar variables de entorno en Render.com
3. ⏳ Reiniciar servicio en Render
4. ⏳ Probar el chat en producción

## Notas Importantes

- Las credenciales se obtienen dinámicamente, por lo que los cambios en variables de entorno se reflejan sin reiniciar (aunque se recomienda reiniciar para asegurar)
- El sistema prioriza el token en memoria sobre las variables de entorno
- Los headers de OpenRouter se agregan automáticamente si detecta que es OpenRouter
- El timeout está configurado a 60 segundos para consultas complejas
