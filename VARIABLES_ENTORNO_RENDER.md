# Variables de Entorno para Render

## 📋 Variables Requeridas para el Web Service

### 🔐 Base de Datos (Automático)
**Render agregará esto automáticamente cuando conectes PostgreSQL:**
- `DATABASE_URL` - Se agrega automáticamente al conectar PostgreSQL en "Connections"
  - Valor: `postgresql://kohde_bd_user:HNzqxWXVZjKxcBvSFRmaa6fAaEsoM3F9@dpg-d5t3u3i4d50c73.../kohde_bd`
  - **NO necesitas agregarla manualmente** si conectas PostgreSQL en "Connections"

### 🚀 Flask (Requeridas)

```
SECRET_KEY
```
**Descripción**: Clave secreta para Flask (sesiones, cookies, etc.)
**Cómo generar**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
**Ejemplo**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2`

```
JWT_SECRET_KEY
```
**Descripción**: Clave secreta para JWT (autenticación)
**Cómo generar**: Usa el mismo comando de arriba o genera otra diferente
**Ejemplo**: `f2e1d0c9b8a7z6y5x4w3v2u1t0s9r8q7p6o5n4m3l2k1j0i9h8g7f6e5d4c3b2a1`

```
DEBUG
```
**Valor**: `false` (en producción)
**Descripción**: Modo debug (desactivado en producción)

---

### 🔍 Google Cloud Vision API (OCR) - Opcional pero Recomendado

```
GOOGLE_CLOUD_PROJECT
```
**Descripción**: ID de tu proyecto en Google Cloud Platform
**Ejemplo**: `mi-proyecto-ocr-123456`
**Cómo obtener**: 
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea o selecciona un proyecto
3. Copia el Project ID

```
GOOGLE_APPLICATION_CREDENTIALS_JSON
```
**Descripción**: Contenido completo del archivo JSON de credenciales (codificado)
**Cómo obtener**:
1. En Google Cloud Console → IAM & Admin → Service Accounts
2. Crea una cuenta de servicio o usa una existente
3. Genera una nueva clave JSON
4. Descarga el archivo JSON
5. Copia TODO el contenido del JSON y pégalo aquí como una sola línea

**Ejemplo** (formato):
```json
{"type":"service_account","project_id":"mi-proyecto","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

**Alternativa** (si prefieres usar archivo):
```
GOOGLE_CREDENTIALS_PATH
```
**Valor**: `/opt/render/.config/gcloud/credentials.json`
**Nota**: Requiere subir el archivo manualmente, menos recomendado

---

### 📱 WhatsApp Business API - Opcional

```
WHATSAPP_ACCESS_TOKEN
```
**Descripción**: Token de acceso de Meta para WhatsApp Business API
**Cómo obtener**:
1. Ve a [Meta for Developers](https://developers.facebook.com/)
2. Crea una app → WhatsApp → Business API
3. Ve a "Getting Started" → Copia el Access Token temporal
4. O genera un token permanente en "System Users"

**Ejemplo**: `EAABsbCS1iHgBO7ZC...` (token largo)

```
WHATSAPP_PHONE_NUMBER_ID
```
**Descripción**: ID del número de teléfono de WhatsApp Business
**Cómo obtener**: En Meta for Developers → WhatsApp → API Setup → Phone Number ID
**Ejemplo**: `123456789012345`

```
WHATSAPP_VERIFY_TOKEN
```
**Descripción**: Token personalizado para verificar el webhook
**Valor**: Cualquier string que elijas (guárdalo bien, lo necesitarás para configurar el webhook)
**Ejemplo**: `mi-token-secreto-whatsapp-2024`
**Recomendación**: Usa algo único y difícil de adivinar

```
WHATSAPP_API_URL
```
**Valor**: `https://graph.facebook.com/v18.0`
**Descripción**: URL base de la API de WhatsApp (puede cambiar según la versión)

---

### 📧 SendGrid (Email) - Opcional

```
SENDGRID_API_KEY
```
**Descripción**: API Key de SendGrid para envío de emails
**Cómo obtener**:
1. Ve a [SendGrid](https://sendgrid.com/)
2. Crea una cuenta o inicia sesión
3. Settings → API Keys → Create API Key
4. Copia la API Key (solo se muestra una vez)

**Ejemplo**: `SG.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz` (token largo)

```
EMAIL_FROM
```
**Valor**: `noreply@tudominio.com`
**Descripción**: Email remitente para los correos enviados
**Nota**: Debe ser un email verificado en SendGrid

---

### ⚙️ Configuración del Sistema

```
STOCK_MINIMUM_THRESHOLD_PERCENTAGE
```
**Valor**: `0.2`
**Descripción**: Porcentaje de amortiguador para stock mínimo (20%)
**Ejemplo**: `0.2` = 20% de buffer

```
IVA_PERCENTAGE
```
**Valor**: `0.15`
**Descripción**: Porcentaje de IVA por defecto (15%)
**Ejemplo**: `0.15` = 15% IVA

```
JWT_ACCESS_TOKEN_EXPIRES
```
**Valor**: `3600`
**Descripción**: Tiempo de expiración del token JWT en segundos (1 hora)
**Ejemplo**: `3600` = 1 hora, `86400` = 24 horas

---

## 📝 Resumen Rápido - Variables Mínimas Necesarias

### Mínimas (sin integraciones externas):
```
SECRET_KEY=<generar>
JWT_SECRET_KEY=<generar>
DEBUG=false
STOCK_MINIMUM_THRESHOLD_PERCENTAGE=0.2
IVA_PERCENTAGE=0.15
```

### Completas (con todas las integraciones):
```
SECRET_KEY=<generar>
JWT_SECRET_KEY=<generar>
DEBUG=false
GOOGLE_CLOUD_PROJECT=<tu-project-id>
GOOGLE_APPLICATION_CREDENTIALS_JSON=<contenido-json-completo>
WHATSAPP_ACCESS_TOKEN=<tu-token>
WHATSAPP_PHONE_NUMBER_ID=<tu-phone-id>
WHATSAPP_VERIFY_TOKEN=<token-personalizado>
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
SENDGRID_API_KEY=<tu-api-key>
EMAIL_FROM=noreply@tudominio.com
STOCK_MINIMUM_THRESHOLD_PERCENTAGE=0.2
IVA_PERCENTAGE=0.15
JWT_ACCESS_TOKEN_EXPIRES=3600
```

---

## 🔧 Cómo Agregar Variables en Render

1. Ve a tu **Web Service** en Render
2. Haz clic en **"Environment"** en el menú lateral
3. Haz clic en **"Add Environment Variable"**
4. Agrega cada variable una por una:
   - **Key**: Nombre de la variable (ej: `SECRET_KEY`)
   - **Value**: Valor de la variable
5. Haz clic en **"Save Changes"**
6. Render reiniciará automáticamente el servicio

---

## ⚠️ Notas Importantes

- **DATABASE_URL**: NO la agregues manualmente si conectaste PostgreSQL en "Connections"
- **SECRET_KEY y JWT_SECRET_KEY**: Deben ser diferentes y seguras
- **GOOGLE_APPLICATION_CREDENTIALS_JSON**: Debe ser el JSON completo en una sola línea
- **WHATSAPP_VERIFY_TOKEN**: Guárdalo bien, lo necesitarás para configurar el webhook
- **SENDGRID_API_KEY**: Solo se muestra una vez al crearla, guárdala bien
- Todas las variables son sensibles: **NO las subas a Git**

---

## ✅ Checklist

- [ ] `SECRET_KEY` generada y agregada
- [ ] `JWT_SECRET_KEY` generada y agregada
- [ ] `DEBUG=false` configurado
- [ ] `DATABASE_URL` agregada automáticamente (al conectar PostgreSQL)
- [ ] Variables de Google Cloud Vision (si usas OCR)
- [ ] Variables de WhatsApp (si usas WhatsApp)
- [ ] Variables de SendGrid (si usas emails)
- [ ] Variables de configuración (`STOCK_MINIMUM_THRESHOLD_PERCENTAGE`, `IVA_PERCENTAGE`)
