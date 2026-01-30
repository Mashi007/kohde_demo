# 📁 Ubicación de Variables de Entorno en el Backend

## 📍 Ubicación del Archivo

Las variables de entorno del backend están en el archivo `.env` en la **raíz del proyecto**:

```
kohde_demo/
├── .env                    ← AQUÍ están las variables
├── config.py              ← Lee las variables de .env
├── app.py
└── ...
```

**Ruta completa**: `c:\Users\PORTATIL\Documents\GitHub\kohde_demo\.env`

## ✅ Variables de OpenRouter Agregadas

Las siguientes variables ya fueron agregadas automáticamente a tu `.env`:

```env
# ========== CONFIGURACIÓN OPENROUTER AI ==========
OPENROUTER_API_KEY=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
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-3.5-turbo

# Opcional pero recomendado por OpenRouter
OPENROUTER_HTTP_REFERER=https://github.com/tu-usuario/kohde_demo
OPENROUTER_X_TITLE=Kohde ERP Restaurantes
```

## ✏️ Cómo Editar Manualmente

### Opción 1: Usar un Editor de Texto

1. Abre el archivo `.env` con cualquier editor de texto (Notepad++, VS Code, etc.)
2. Busca la sección `# ========== CONFIGURACIÓN OPENROUTER AI ==========`
3. Edita las variables según necesites
4. Guarda el archivo

### Opción 2: Usar PowerShell (Windows)

```powershell
# Ver el contenido del .env
Get-Content .env

# Agregar una variable nueva
Add-Content .env "NUEVA_VARIABLE=valor"

# Editar una variable existente (reemplazar)
(Get-Content .env) -replace 'OPENAI_MODEL=.*', 'OPENAI_MODEL=openai/gpt-4o' | Set-Content .env
```

### Opción 3: Usar el Script Automático

```bash
python scripts/agregar_variables_openrouter.py
```

## 🔄 Cómo se Carga el .env

El archivo `.env` se carga automáticamente cuando inicia la aplicación Flask gracias a `python-dotenv`:

```python
# En config.py (línea 6)
from dotenv import load_dotenv
load_dotenv()  # ← Esto carga el .env automáticamente
```

## 📋 Variables Importantes del Sistema

Tu `.env` contiene variables para diferentes servicios:

### Base de Datos
```env
DATABASE_URL=postgresql://...
# o
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_restaurantes
DB_USER=postgres
DB_PASSWORD=...
```

### OpenRouter / AI (✅ Ya configurado)
```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-3.5-turbo
```

### WhatsApp
```env
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
```

### Email
```env
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=...
# o
GMAIL_SMTP_USER=...
GMAIL_SMTP_PASSWORD=...
```

## 🔒 Seguridad

⚠️ **IMPORTANTE**:
- El archivo `.env` está en `.gitignore` (NO se sube a Git)
- **NUNCA** compartas tu `.env` públicamente
- **NUNCA** subas el `.env` a repositorios públicos
- El backup `.env.backup` también está protegido

## 🔄 Reiniciar el Servidor

Después de modificar el `.env`, **debes reiniciar el servidor Flask** para que los cambios surtan efecto:

```bash
# Detener el servidor (Ctrl+C)
# Luego iniciarlo de nuevo
python app.py
# o
flask run
```

## 📝 Cambiar el Modelo de AI

Para cambiar el modelo de OpenRouter, edita esta línea en el `.env`:

```env
# Modelo económico
OPENAI_MODEL=openai/gpt-3.5-turbo

# Modelo más potente
OPENAI_MODEL=openai/gpt-4o

# Modelo muy potente
OPENAI_MODEL=anthropic/claude-3.5-sonnet
```

Ver todos los modelos: https://openrouter.ai/models

## ✅ Verificar que las Variables Están Cargadas

Puedes verificar que las variables están cargadas correctamente:

```bash
# Ver configuración actual
python -c "from config import Config; print(f'Modelo: {Config.OPENAI_MODEL}'); print(f'Base URL: {Config.OPENAI_BASE_URL}')"
```

O usar el endpoint de la API:
```bash
GET /api/configuracion/ai
```

## 🆘 Problemas Comunes

### Las variables no se cargan
1. Verifica que el archivo se llama exactamente `.env` (con el punto al inicio)
2. Verifica que está en la raíz del proyecto
3. Reinicia el servidor Flask

### El token no funciona
1. Verifica que el token está completo y correcto
2. Verifica que no hay espacios extra al inicio/final
3. Usa el endpoint `/api/configuracion/ai/verificar` para probar

### Variables se pierden al reiniciar
- Si configuraste el token vía API (`PUT /api/configuracion/ai/token`), solo se guarda en memoria
- Para hacerlo permanente, agrégalo al `.env` como se muestra arriba

## 📚 Referencias

- Documentación de OpenRouter: https://openrouter.ai/docs
- Modelos disponibles: https://openrouter.ai/models
- Variables de entorno en Flask: https://flask.palletsprojects.com/en/latest/config/
