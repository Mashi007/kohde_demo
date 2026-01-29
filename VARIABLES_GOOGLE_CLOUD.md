# 🔐 Variables de Entorno - Google Cloud Vision API

## 📋 Variables Requeridas en Render (Web Service)

### ✅ Variables Esenciales (Obligatorias)

```bash
# Proyecto de Google Cloud
GOOGLE_CLOUD_PROJECT=ocrtesting-485721

# Ruta al archivo de credenciales (Render lo crea automáticamente)
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-credentials.json
```

---

### 🔄 Variables Automáticas de Render (Workload Identity)

Estas variables se configuran automáticamente cuando conectas Google Cloud en Render. **No necesitas configurarlas manualmente**, pero puedes verlas:

```bash
# Provider de Workload Identity
WORKLOAD_IDENTITY_PROVIDER=projects/1091415852286/locations/global/workloadIdentityPools/render-pool/providers/render-provider

# Email de la cuenta de servicio
SERVICE_ACCOUNT_EMAIL=render-ocr-sa@ocrtesting-485721.iam.gserviceaccount.com

# ID del servicio en Render
RENDER_SERVICE_ID=srv-d5i47anuibrs739du3o0
```

---

## 📝 Variables Opcionales (Alternativas)

Si **NO** usas Workload Identity, puedes usar estas variables alternativas:

```bash
# Opción 1: Ruta a archivo JSON local (solo desarrollo local)
GOOGLE_CREDENTIALS_PATH=/ruta/al/archivo.json

# Opción 2: Contenido JSON completo como string (para Render manual)
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"ocrtesting-485721",...}
```

---

## ✅ Configuración Actual (Tu Proyecto)

### Variables que DEBES tener en Render:

```
GOOGLE_CLOUD_PROJECT=ocrtesting-485721
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-credentials.json
```

### Variables que Render configura automáticamente:

```
WORKLOAD_IDENTITY_PROVIDER=projects/1091415852286/locations/global/workloadIdentityPools/render-pool/providers/render-provider
SERVICE_ACCOUNT_EMAIL=render-ocr-sa@ocrtesting-485721.iam.gserviceaccount.com
RENDER_SERVICE_ID=srv-d5i47anuibrs739du3o0
```

---

## 🔧 Cómo Configurar en Render

### Paso 1: Ir a tu Web Service
1. Ve a tu servicio en Render: https://dashboard.render.com
2. Selecciona tu Web Service
3. Ve a la pestaña **"Environment"**

### Paso 2: Agregar Variables

Haz clic en **"Add Environment Variable"** y agrega:

| Variable | Valor |
|----------|-------|
| `GOOGLE_CLOUD_PROJECT` | `ocrtesting-485721` |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/tmp/gcloud-credentials.json` |

### Paso 3: Conectar Google Cloud (Workload Identity)

1. En Render, ve a **"Settings"** → **"Connected Accounts"**
2. Conecta tu cuenta de Google Cloud
3. Render configurará automáticamente las otras variables

---

## 📋 Resumen Rápido

### Mínimo Necesario:
```bash
GOOGLE_CLOUD_PROJECT=ocrtesting-485721
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-credentials.json
```

### Con Workload Identity (Automático):
```bash
GOOGLE_CLOUD_PROJECT=ocrtesting-485721
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-credentials.json
WORKLOAD_IDENTITY_PROVIDER=projects/1091415852286/locations/global/workloadIdentityPools/render-pool/providers/render-provider
SERVICE_ACCOUNT_EMAIL=render-ocr-sa@ocrtesting-485721.iam.gserviceaccount.com
RENDER_SERVICE_ID=srv-d5i47anuibrs739du3o0
```

---

## ✅ Verificación

Para verificar que las variables están configuradas:

1. Ve a Render Dashboard → Tu Web Service → Environment
2. Debes ver al menos estas 2 variables:
   - `GOOGLE_CLOUD_PROJECT`
   - `GOOGLE_APPLICATION_CREDENTIALS`

3. Las otras 3 variables aparecen automáticamente si Workload Identity está conectado

---

## 🚨 Importante

- **NO** necesitas configurar `GOOGLE_CREDENTIALS_PATH` si usas Workload Identity
- **NO** necesitas configurar `GOOGLE_APPLICATION_CREDENTIALS_JSON` si usas Workload Identity
- Render crea automáticamente el archivo en `/tmp/gcloud-credentials.json`
- El código detecta automáticamente las credenciales

---

## 📝 Notas

- **Workload Identity** es más seguro que archivos JSON estáticos
- Render maneja la rotación de credenciales automáticamente
- No necesitas mantener archivos JSON manualmente
- El código ya está preparado para usar este método

---

¡Con estas variables tu aplicación podrá usar Google Cloud Vision API! 🎉
