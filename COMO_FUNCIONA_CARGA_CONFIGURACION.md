# 🔄 Cómo Funciona la Carga de Configuración de AI

## ✅ Sí, las Variables del `.env` se Cargarán Automáticamente

### 📍 Flujo de Carga

```
1. Servidor Flask inicia
   ↓
2. python-dotenv carga el archivo .env
   ↓
3. Las variables se cargan en Config.OPENROUTER_API_KEY, etc.
   ↓
4. Frontend llama a GET /api/configuracion/ai
   ↓
5. Backend lee las variables del .env
   ↓
6. Frontend muestra la configuración en la interfaz
```

## 🔍 Orden de Prioridad

El sistema busca la configuración en este orden:

1. **Token en memoria** (si se guardó vía API `PUT /api/configuracion/ai/token`)
2. **Variables de entorno** (del archivo `.env`)
   - `OPENROUTER_API_KEY` (prioridad)
   - `OPENAI_API_KEY` (fallback)

## 📱 Qué Verás en el Frontend

Cuando el frontend carga la configuración (`GET /api/configuracion/ai`), verás:

### Si las Variables Están en `.env`:

```json
{
  "estado": "configurado",
  "openai_api_key_configured": true,
  "openai_api_key_preview": "sk-or-v1-9...5cc",
  "openai_model": "openai/gpt-3.5-turbo",
  "openai_base_url": "https://openrouter.ai/api/v1",
  "proveedor": "OpenRouter",
  "es_openrouter": true,
  "token_en_memoria": false
}
```

### En la Interfaz Verás:

- **Estado**: ✅ "Configurado" (en lugar de "No configurado")
- **API Key**: Preview del token (primeros 10 + últimos 4 caracteres)
- **Modelo**: `openai/gpt-3.5-turbo`
- **Base URL**: `https://openrouter.ai/api/v1`
- **Proveedor**: OpenRouter

## 🔄 Dos Formas de Configurar

### Opción 1: Variables de Entorno (`.env`) - ✅ RECOMENDADO

**Ventajas:**
- ✅ Permanente (sobrevive reinicios)
- ✅ Seguro (no se sube a Git)
- ✅ Funciona en producción (Render, etc.)

**Cómo funciona:**
1. Agregas las variables al `.env`
2. Reinicias el servidor Flask
3. El frontend automáticamente muestra la configuración

### Opción 2: Interfaz del Frontend (Temporal)

**Ventajas:**
- ✅ Rápido para pruebas
- ✅ No requiere reiniciar servidor

**Desventajas:**
- ⚠️ Se pierde al reiniciar el servidor
- ⚠️ Solo funciona en desarrollo local

## 📋 Lo que Debes Hacer

### Para Desarrollo Local:

1. ✅ **Ya está hecho**: Variables agregadas al `.env`
2. 🔄 **Reinicia el servidor Flask**:
   ```bash
   # Detener servidor (Ctrl+C)
   python app.py
   ```
3. 🔄 **Recarga el frontend** (F5 o Ctrl+R)
4. ✅ **Verás**: La configuración cargada automáticamente

### Para Producción (Render):

1. Ve a tu proyecto en Render.com
2. Settings → Environment Variables
3. Agrega las mismas variables:
   ```
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=openai/gpt-3.5-turbo
   OPENROUTER_HTTP_REFERER=https://github.com/Mashi007/kohde_demo.git
   OPENROUTER_X_TITLE=Kohde ERP Restaurantes
   ```
4. Render reiniciará automáticamente

## 🧪 Verificar que se Cargó

### Opción 1: Ver en el Frontend
- Recarga la página de configuración de AI
- Deberías ver "Estado: Configurado" en verde
- El preview del token debería aparecer

### Opción 2: Endpoint API
```bash
GET /api/configuracion/ai
```

Respuesta esperada:
```json
{
  "estado": "configurado",
  "openai_api_key_configured": true,
  "openai_api_key_preview": "sk-or-v1-9...5cc",
  "proveedor": "OpenRouter"
}
```

## ⚠️ Importante

### Si No Se Carga:

1. **Verifica que reiniciaste el servidor Flask**
   - Las variables del `.env` solo se cargan al iniciar Flask

2. **Verifica que el `.env` está en la raíz del proyecto**
   ```
   kohde_demo/
   ├── .env          ← Debe estar aquí
   ├── app.py
   └── ...
   ```

3. **Verifica el formato del `.env`**
   - Sin espacios alrededor del `=`
   - Sin comillas innecesarias
   - Una variable por línea

4. **Verifica que las variables tienen los nombres correctos**
   - `OPENROUTER_API_KEY` (no `OPENAI_API_KEY` para OpenRouter)
   - `OPENAI_BASE_URL` (sí, aunque sea OpenRouter)
   - `OPENAI_MODEL` (sí, aunque sea OpenRouter)

## ✅ Resumen

**SÍ, las variables del `.env` se cargarán automáticamente en el frontend** cuando:

1. ✅ El servidor Flask se reinicie (para cargar el `.env`)
2. ✅ El frontend llame al endpoint `/api/configuracion/ai`
3. ✅ La interfaz mostrará "Estado: Configurado" automáticamente

**No necesitas ingresar el token manualmente en el frontend** si ya está en el `.env` y reiniciaste el servidor.
