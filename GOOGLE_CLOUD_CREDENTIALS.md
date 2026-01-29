# 🔐 Configuración de Credenciales de Google Cloud Vision

## ❌ Problema con GOOGLE_CREDENTIALS_PATH

**Valor actual en Render**:
```
GOOGLE_CREDENTIALS_PATH = /opt/render/.config/gcloud/credentials.json
```

**Problema**: Este path **NO funcionará** en Render porque:
- Render no tiene acceso a ese directorio por defecto
- Necesitarías subir el archivo manualmente
- Es más complicado de mantener

---

## ✅ Solución Recomendada: GOOGLE_APPLICATION_CREDENTIALS_JSON

**Mejor opción**: Usar `GOOGLE_APPLICATION_CREDENTIALS_JSON` con el contenido del JSON como string.

### Cómo Obtener las Credenciales:

1. **Ve a Google Cloud Console**:
   - https://console.cloud.google.com/
   - Selecciona tu proyecto (o crea uno nuevo)

2. **Habilita Cloud Vision API**:
   - Ve a "APIs y servicios" → "Biblioteca"
   - Busca "Cloud Vision API"
   - Haz clic en "Habilitar"

3. **Crea una Cuenta de Servicio**:
   - Ve a "IAM y administración" → "Cuentas de servicio"
   - Haz clic en "+ Crear cuenta de servicio"
   - Nombre: `erp-vision-api` (o el que prefieras)
   - Rol: "Cloud Vision API User" o "Editor"
   - Haz clic en "Listo"

4. **Genera la Clave JSON**:
   - En la lista de cuentas de servicio, haz clic en la que acabas de crear
   - Ve a la pestaña "Claves"
   - Haz clic en "Agregar clave" → "Crear nueva clave"
   - Selecciona "JSON"
   - Haz clic en "Crear"
   - **Se descargará un archivo JSON** (guárdalo seguro)

5. **Copia el Contenido del JSON**:
   - Abre el archivo JSON descargado
   - Copia **TODO** el contenido
   - Debe verse algo así:
   ```json
   {
     "type": "service_account",
     "project_id": "tu-project-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "...",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

---

## 🔧 Configuración en Render

### Opción 1: Usar GOOGLE_APPLICATION_CREDENTIALS_JSON (Recomendado)

1. **Elimina** la variable `GOOGLE_CREDENTIALS_PATH`

2. **Agrega** nueva variable:
   ```
   KEY: GOOGLE_APPLICATION_CREDENTIALS_JSON
   VALUE: (pega TODO el contenido del JSON en una sola línea)
   ```

   **Ejemplo del valor**:
   ```
   {"type":"service_account","project_id":"tu-project-id","private_key_id":"abc123","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n","client_email":"erp-vision-api@tu-project.iam.gserviceaccount.com","client_id":"123456789","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/erp-vision-api%40tu-project.iam.gserviceaccount.com"}
   ```

   **Importante**: Debe ser **una sola línea**, sin saltos de línea.

3. **Actualiza** `GOOGLE_CLOUD_PROJECT`:
   ```
   KEY: GOOGLE_CLOUD_PROJECT
   VALUE: tu-project-id-real (el mismo que está en el JSON)
   ```

---

### Opción 2: Mantener GOOGLE_CREDENTIALS_PATH (No Recomendado)

Si realmente quieres usar `GOOGLE_CREDENTIALS_PATH`:

1. Necesitarías subir el archivo JSON a Render (complicado)
2. O usar un servicio de almacenamiento externo (S3, etc.)
3. Más complejo y menos recomendado

---

## 📋 Resumen de Variables para Google Cloud

### Variables Necesarias:

```
GOOGLE_CLOUD_PROJECT = tu-project-id-real
GOOGLE_APPLICATION_CREDENTIALS_JSON = (contenido-completo-del-json-en-una-linea)
```

### Variables a Eliminar:

```
GOOGLE_CREDENTIALS_PATH ❌ (eliminar)
```

---

## ✅ Pasos en Render

1. **Elimina** `GOOGLE_CREDENTIALS_PATH`
2. **Agrega** `GOOGLE_APPLICATION_CREDENTIALS_JSON` con el contenido del JSON
3. **Actualiza** `GOOGLE_CLOUD_PROJECT` con tu Project ID real
4. **Guarda** los cambios
5. Render reiniciará automáticamente

---

## 🧪 Verificación

Después de configurar, prueba el OCR:
- Sube una factura por WhatsApp o por la API
- Debería procesarse correctamente con Google Cloud Vision
- Revisa los logs si hay errores

---

## ⚠️ Seguridad

- **NUNCA** subas el archivo JSON a Git
- **NUNCA** compartas las credenciales
- El JSON contiene claves privadas - trátalo como información sensible
- Si se compromete, elimina la cuenta de servicio y crea una nueva
