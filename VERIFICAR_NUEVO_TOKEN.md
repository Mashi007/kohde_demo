# ✅ Verificación del Nuevo Token en Producción

## 📋 Estado Actual

Has generado un nuevo token y lo has configurado en Render.com. Ahora necesitamos verificar que todo funcione.

## ⚠️ Nota Importante

El script de diagnóstico local (`diagnostico_error_401.py`) está usando el token del archivo `.env` local, **NO** el token de producción en Render.com.

Por eso todavía muestra el token antiguo (`...45cc`).

## ✅ Pasos para Verificar que Funcione

### 1. Verificar en Render.com

1. Ve a **Render Dashboard** → Tu servicio
2. Ve a **Environment**
3. Verifica que `OPENROUTER_API_KEY` tenga el **nuevo token** (no el que termina en `45cc`)
4. Verifica que el token comience con `sk-or-v1-`

### 2. Reiniciar el Servicio

**IMPORTANTE**: Después de cambiar variables de entorno, debes reiniciar el servicio:

1. En Render Dashboard → Tu servicio
2. Ve a la sección **"Manual Deploy"** o **"Events"**
3. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**
4. O simplemente espera el despliegue automático (puede tardar 1-2 minutos)

### 3. Probar el Chat en Producción

Una vez reiniciado el servicio:

1. Ve a **https://kohde-demo-1.onrender.com/chat**
2. Envía un mensaje de prueba: "hola"
3. Deberías recibir una respuesta del AI (sin error 401)

### 4. Verificar Logs (Si Hay Problemas)

Si el error 401 persiste:

1. Ve a Render Dashboard → Tu servicio → **Logs**
2. Busca errores relacionados con:
   - "401"
   - "User not found"
   - "Error al llamar a la API"

## 🔍 Verificación del Token Local (Opcional)

Si quieres actualizar también tu `.env` local con el nuevo token:

1. Edita el archivo `.env` local
2. Reemplaza `OPENROUTER_API_KEY` con el nuevo token
3. **NO** hagas commit de este archivo (está en `.gitignore`)

## ✅ Checklist

- [x] Nuevo token generado en OpenRouter
- [x] Token configurado en Render.com (variables de entorno)
- [ ] Servicio reiniciado en Render.com
- [ ] Chat probado en producción
- [ ] Verificado que funciona sin error 401

## 🎯 Próximo Paso

**Reinicia el servicio en Render.com** y luego prueba el chat en producción.

Si después de reiniciar el servicio el error 401 persiste, verifica:
1. Que el nuevo token tenga créditos en OpenRouter
2. Que el token sea correcto (copiado completo)
3. Los logs de Render para ver el error específico
