# 🔑 Generar Clave JSON para Cuenta de Servicio

## 📋 Estado Actual

Veo que tienes:
- ✅ Cuenta de servicio creada: `C_whatsapp`
- ✅ Email: `c-whatsapp@cobranzas-485720.iam.gserviceaccount.com`
- ✅ Estado: Habilitado
- ❌ **ID de clave**: "No hay claves" ← **Necesitas generar una**

---

## 🔧 Pasos para Generar la Clave JSON

### Paso 1: Abrir la Cuenta de Servicio

1. En la tabla, haz clic en el **email** de la cuenta:
   ```
   c-whatsapp@cobranzas-485720.iam.gserviceaccount.com
   ```
   O haz clic en el menú de **"Acciones"** (tres puntos verticales) → **"Administrar claves"**

### Paso 2: Ir a la Pestaña "Claves"

1. Una vez dentro de la cuenta de servicio, busca la pestaña **"Claves"** (Keys)
2. Haz clic en esa pestaña

### Paso 3: Generar Nueva Clave

1. Haz clic en el botón **"Agregar clave"** o **"Crear nueva clave"**
2. Selecciona el tipo: **"JSON"** (NO OAuth)
3. Haz clic en **"Crear"**

### Paso 4: Descargar el Archivo

1. Se descargará automáticamente un archivo JSON
2. **Guárdalo seguro** (no lo subas a Git)
3. El archivo tendrá un nombre como: `cobranzas-485720-xxxxx.json`

---

## 📝 Contenido del Archivo JSON

El archivo descargado tendrá este formato:

```json
{
  "type": "service_account",
  "project_id": "cobranzas-485720",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "c-whatsapp@cobranzas-485720.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/c-whatsapp%40cobranzas-485720.iam.gserviceaccount.com"
}
```

---

## 🔧 Configurar en Render

### Paso 1: Copiar el Contenido del JSON

1. Abre el archivo JSON descargado
2. Selecciona **TODO** el contenido (Ctrl+A)
3. Copia (Ctrl+C)
4. **Conviértelo a una sola línea** (elimina saltos de línea)

### Paso 2: Configurar en Render

1. Ve a tu **Web Service** en Render → **Environment**
2. **Elimina** (si existe):
   ```
   GOOGLE_CREDENTIALS_PATH ❌
   ```
3. **Actualiza**:
   ```
   GOOGLE_CLOUD_PROJECT = cobranzas-485720
   ```
4. **Agrega nueva variable**:
   ```
   KEY: GOOGLE_APPLICATION_CREDENTIALS_JSON
   VALUE: (pega TODO el JSON en UNA SOLA LÍNEA)
   ```

**Ejemplo del valor** (debe ser una sola línea):
```
{"type":"service_account","project_id":"cobranzas-485720","private_key_id":"abc123","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n","client_email":"c-whatsapp@cobranzas-485720.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/c-whatsapp%40cobranzas-485720.iam.gserviceaccount.com"}
```

---

## ✅ Verificación

Después de configurar:
1. Guarda los cambios en Render
2. Render reiniciará automáticamente
3. Prueba subir una factura por WhatsApp o API
4. Debería procesarse con OCR correctamente

---

## ⚠️ Importante

- **NO subas el archivo JSON a Git**
- **Guarda el archivo JSON en un lugar seguro**
- **Si se compromete**, elimina la clave y genera una nueva
- El JSON debe estar en **UNA SOLA LÍNEA** en Render

---

## 🎯 Resumen

1. ✅ Cuenta de servicio creada
2. ⏳ **Generar clave JSON** (hacer ahora)
3. ⏳ Configurar en Render con `GOOGLE_APPLICATION_CREDENTIALS_JSON`
4. ⏳ Habilitar Cloud Vision API

¿Necesitas ayuda para convertir el JSON a una sola línea o configurarlo en Render?
