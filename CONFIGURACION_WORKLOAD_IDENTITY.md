# 🔐 Configuración con Workload Identity Federation (Render)

## ✅ Variables que Tienes Configuradas

```
GOOGLE_CLOUD_PROJECT=ocrtesting-485721 ✅
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcloud-credentials.json ✅
WORKLOAD_IDENTITY_PROVIDER=projects/1091415852286/locations/global/workloadIdentityPools/render-pool/providers/render-provider ✅
SERVICE_ACCOUNT_EMAIL=render-ocr-sa@ocrtesting-485721.iam.gserviceaccount.com ✅
RENDER_SERVICE_ID=srv-d5i47anuibrs739du3o0 ✅
```

---

## 🎯 Cómo Funciona Workload Identity

Render crea automáticamente el archivo de credenciales en `/tmp/gcloud-credentials.json` cuando tienes Workload Identity configurado.

El código ya está actualizado para detectar este archivo automáticamente.

---

## ✅ Configuración en Render

### Variables que Debes Tener:

```
GOOGLE_CLOUD_PROJECT = ocrtesting-485721
GOOGLE_APPLICATION_CREDENTIALS = /tmp/gcloud-credentials.json
```

**Las otras variables** (`WORKLOAD_IDENTITY_PROVIDER`, `SERVICE_ACCOUNT_EMAIL`, `RENDER_SERVICE_ID`) son **internas de Render** y se configuran automáticamente cuando conectas Google Cloud.

---

## 🔧 Verificación

### 1. Verificar que el Archivo Existe

El código verificará automáticamente si `/tmp/gcloud-credentials.json` existe.

### 2. Verificar Permisos de la Cuenta de Servicio

Asegúrate de que la cuenta `render-ocr-sa@ocrtesting-485721.iam.gserviceaccount.com` tenga:
- **Rol**: `Cloud Vision API User` o `Editor`
- **Cloud Vision API**: Habilitada en el proyecto

---

## 📋 Checklist

- [x] `GOOGLE_CLOUD_PROJECT` configurado ✅
- [x] `GOOGLE_APPLICATION_CREDENTIALS` configurado ✅
- [ ] Verificar que la cuenta de servicio tiene permisos de Vision API
- [ ] Verificar que Cloud Vision API está habilitada
- [ ] Probar OCR subiendo una factura

---

## 🧪 Cómo Probar

1. Sube una factura por WhatsApp o por la API
2. Revisa los logs del Web Service en Render
3. Deberías ver que el OCR se ejecuta correctamente
4. Si hay errores, revisa los permisos de la cuenta de servicio

---

## ⚠️ Si No Funciona

Si el archivo `/tmp/gcloud-credentials.json` no existe automáticamente:

1. Verifica que Workload Identity esté correctamente configurado en Render
2. O usa la alternativa: `GOOGLE_APPLICATION_CREDENTIALS_JSON` con el contenido del JSON

---

## 📝 Notas

- **Workload Identity** es más seguro que archivos JSON estáticos
- Render maneja la rotación de credenciales automáticamente
- No necesitas mantener archivos JSON manualmente
- El código ya está preparado para usar este método

---

¡Con esta configuración deberías estar listo! El código detectará automáticamente las credenciales de Render.
