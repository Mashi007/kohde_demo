# Configuración de OpenRouter para AI

## ✅ Token Configurado

Tu token de OpenRouter ya está configurado en el sistema:
- **Token**: `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`

## 📋 Configuración Actual

El sistema está configurado para usar OpenRouter con los siguientes valores por defecto:

- **Base URL**: `https://openrouter.ai/api/v1`
- **Modelo por defecto**: `openai/gpt-3.5-turbo`
- **Token**: Configurado en memoria (se puede actualizar vía API)

## 🔧 Variables de Entorno Recomendadas

Para hacer la configuración permanente (sobrevive reinicios del servidor), agrega estas variables a tu archivo `.env`:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=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
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-3.5-turbo

# Opcional pero recomendado por OpenRouter
OPENROUTER_HTTP_REFERER=https://github.com/tu-usuario/kohde_demo
OPENROUTER_X_TITLE=Kohde ERP Restaurantes
```

## 🤖 Modelos Disponibles en OpenRouter

OpenRouter permite usar múltiples modelos. Algunos ejemplos populares:

### Modelos OpenAI
- `openai/gpt-4o` - GPT-4 Optimizado (más rápido y económico)
- `openai/gpt-4-turbo` - GPT-4 Turbo
- `openai/gpt-3.5-turbo` - GPT-3.5 Turbo (más económico)

### Modelos Anthropic (Claude)
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet (muy potente)
- `anthropic/claude-3-opus` - Claude 3 Opus
- `anthropic/claude-3-haiku` - Claude 3 Haiku (rápido y económico)

### Modelos Meta (Llama)
- `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B
- `meta-llama/llama-3.1-8b-instruct` - Llama 3.1 8B (más económico)

### Otros Modelos
- `google/gemini-pro-1.5` - Google Gemini Pro
- `mistralai/mistral-large` - Mistral Large

**Nota**: Puedes ver todos los modelos disponibles en: https://openrouter.ai/models

## 📡 Cómo Actualizar la Configuración

### Opción 1: Vía API (Temporal - se pierde al reiniciar)

```bash
PUT /api/configuracion/ai/token
Content-Type: application/json

{
  "api_key": "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",
  "modelo": "openai/gpt-3.5-turbo",
  "base_url": "https://openrouter.ai/api/v1"
}
```

### Opción 2: Variables de Entorno (Permanente)

Agrega las variables al archivo `.env` como se muestra arriba.

## 🧪 Probar la Configuración

### Verificar Configuración Actual
```bash
GET /api/configuracion/ai
```

### Verificar que el Token Funciona
```bash
GET /api/configuracion/ai/verificar
```

### Enviar Mensaje de Prueba
```bash
POST /api/configuracion/ai/probar
Content-Type: application/json

{
  "mensaje": "Hola, ¿puedes responder con OK?"
}
```

## 💡 Información Adicional de OpenRouter

### Headers Requeridos

OpenRouter requiere estos headers en las peticiones:

1. **Authorization**: `Bearer sk-or-v1-...` ✅ (Ya configurado)
2. **HTTP-Referer**: URL de tu aplicación (Opcional pero recomendado)
3. **X-Title**: Nombre de tu aplicación (Opcional)

### Precios

Los precios varían según el modelo. OpenRouter cobra por:
- **Input tokens**: Tokens que envías al modelo
- **Output tokens**: Tokens que el modelo genera

Puedes ver los precios actualizados en: https://openrouter.ai/models

### Límites

- OpenRouter tiene límites de rate según tu plan
- El plan gratuito tiene límites más restrictivos
- Puedes ver tu uso y límites en: https://openrouter.ai/keys

## 🔒 Seguridad

**IMPORTANTE**: 
- ⚠️ El token es sensible. No lo compartas públicamente.
- ✅ Ya está configurado en memoria del servidor
- ✅ Para producción, usa variables de entorno (`.env` no se sube a git)
- ✅ El token se muestra parcialmente en la API de configuración (primeros 10 y últimos 4 caracteres)

## 📚 Documentación

- **OpenRouter Docs**: https://openrouter.ai/docs
- **API Reference**: https://openrouter.ai/docs/api-reference
- **Modelos Disponibles**: https://openrouter.ai/models

## ✅ Checklist de Configuración

- [x] Token configurado
- [x] Base URL configurada (OpenRouter)
- [x] Validación de tokens OpenRouter implementada
- [x] Headers específicos de OpenRouter agregados
- [ ] Variables de entorno configuradas (recomendado)
- [ ] Modelo seleccionado según necesidades
- [ ] Prueba de funcionamiento realizada

## 🎯 Próximos Pasos

1. **Configurar variables de entorno** en `.env` para hacer la configuración permanente
2. **Seleccionar el modelo** que mejor se adapte a tus necesidades (costo vs rendimiento)
3. **Probar la configuración** usando los endpoints de verificación
4. **Revisar límites y precios** en tu cuenta de OpenRouter
