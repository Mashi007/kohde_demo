# ✅ Verificación de Variables de Entorno - Web Service

## 📋 Variables Configuradas Actualmente

### ✅ Variables Correctas:

1. **DATABASE_URL** ✅
   - Valor: `postgresql://kohde_bd_user:HNzqxWXVZjKxcBvSFRmaa6fAaEsoM3F9@dpg-25+30211d50c739.render.com/kohde_bd`
   - Estado: ✅ CORRECTO - Se agregó automáticamente al conectar PostgreSQL

2. **SECRET_KEY** ✅
   - Valor: `773c509dcb712d5acd1c672920209114`
   - Estado: ✅ CORRECTO - Clave generada

3. **JWT_SECRET_KEY** ✅
   - Valor: `6e8b28ecacb2d2d2e66e9bf8afa94c6a`
   - Estado: ✅ CORRECTO - Clave generada

4. **DEBUG** ✅
   - Valor: `False`
   - Estado: ✅ CORRECTO - Producción

5. **STOCK_MINIMUM_THRESHOLD_PERCENTAGE** ✅
   - Valor: `0.2`
   - Estado: ✅ CORRECTO

---

### ⚠️ Variables con Placeholders (Necesitan Valores Reales):

6. **GOOGLE_CLOUD_PROJECT** ⚠️
   - Valor: `<tu-project-id>`
   - Estado: ⚠️ PLACEHOLDER - Necesita tu Project ID real de Google Cloud
   - Acción: Reemplazar con tu Project ID real

7. **GOOGLE_CREDENTIALS_PATH** ⚠️
   - Valor: `/opt/render/.config/gcloud/credentials.json`
   - Estado: ⚠️ PROBLEMA - Este path no funcionará en Render
   - Acción: Mejor usar `GOOGLE_APPLICATION_CREDENTIALS_JSON` con el contenido del JSON

8. **WHATSAPP_ACCESS_TOKEN** ⚠️
   - Valor: `<tu-token>`
   - Estado: ⚠️ PLACEHOLDER - Necesita token real de Meta
   - Acción: Reemplazar con tu token real

9. **WHATSAPP_PHONE_NUMBER_ID** ⚠️
   - Valor: `<tu-phone-id>`
   - Estado: ⚠️ PLACEHOLDER - Necesita ID real
   - Acción: Reemplazar con tu Phone Number ID real

10. **WHATSAPP_VERIFY_TOKEN** ⚠️
    - Valor: `<token-personalizado>`
    - Estado: ⚠️ PLACEHOLDER - Necesita token personalizado
    - Acción: Crear un token único (ej: `mi-token-secreto-2024`)

---

### ❌ Variables que NO Deberían Estar:

11. **DB_PASSWORD** ❌
    - Valor: `HNzqxWXVZjKxcBvSFRmaa6fAaEsoM3F9`
    - Estado: ❌ NO NECESARIA - Ya está en `DATABASE_URL`
    - Acción: Puedes eliminarla (es redundante)

---

### ✅ Variables que FALTAN (Recomendadas):

12. **IVA_PERCENTAGE** ⚠️
    - Valor recomendado: `0.15`
    - Estado: FALTA - Tiene valor por defecto pero es mejor configurarla

13. **JWT_ACCESS_TOKEN_EXPIRES** ⚠️
    - Valor recomendado: `3600`
    - Estado: FALTA - Tiene valor por defecto pero es mejor configurarla

14. **EMAIL_FROM** ⚠️
    - Valor recomendado: `noreply@tudominio.com`
    - Estado: FALTA - Solo si usas SendGrid

15. **SENDGRID_API_KEY** ⚠️
    - Valor: Tu API Key de SendGrid
    - Estado: FALTA - Solo si usas emails

---

## 🔧 Correcciones Necesarias

### 1. Eliminar Variable Redundante:
```
DB_PASSWORD → ELIMINAR (ya está en DATABASE_URL)
```

### 2. Reemplazar Placeholders:

**GOOGLE_CLOUD_PROJECT**:
```
Cambiar: <tu-project-id>
Por: tu-project-id-real-de-google-cloud
```

**GOOGLE_CREDENTIALS_PATH** (Mejor usar JSON):
```
Eliminar: GOOGLE_CREDENTIALS_PATH
Agregar: GOOGLE_APPLICATION_CREDENTIALS_JSON
Valor: (contenido completo del JSON de credenciales en una línea)
```

**WHATSAPP_ACCESS_TOKEN**:
```
Cambiar: <tu-token>
Por: tu-token-real-de-meta
```

**WHATSAPP_PHONE_NUMBER_ID**:
```
Cambiar: <tu-phone-id>
Por: tu-phone-number-id-real
```

**WHATSAPP_VERIFY_TOKEN**:
```
Cambiar: <token-personalizado>
Por: un-token-unico-que-elijas (ej: kohde-whatsapp-2024)
```

### 3. Agregar Variables Faltantes:

```
IVA_PERCENTAGE = 0.15
JWT_ACCESS_TOKEN_EXPIRES = 3600
```

---

## ✅ Configuración Final Recomendada

### Variables Esenciales (Mínimas):
```
DATABASE_URL = (automático) ✅
SECRET_KEY = 773c509dcb712d5acd1c672920209114 ✅
JWT_SECRET_KEY = 6e8b28ecacb2d2d2e66e9bf8afa94c6a ✅
DEBUG = False ✅
STOCK_MINIMUM_THRESHOLD_PERCENTAGE = 0.2 ✅
IVA_PERCENTAGE = 0.15 ⚠️ AGREGAR
```

### Variables Opcionales (Si usas las funcionalidades):
```
GOOGLE_CLOUD_PROJECT = (tu-project-id-real) ⚠️ REEMPLAZAR
GOOGLE_APPLICATION_CREDENTIALS_JSON = (contenido-json-completo) ⚠️ AGREGAR
WHATSAPP_ACCESS_TOKEN = (tu-token-real) ⚠️ REEMPLAZAR
WHATSAPP_PHONE_NUMBER_ID = (tu-phone-id-real) ⚠️ REEMPLAZAR
WHATSAPP_VERIFY_TOKEN = (token-personalizado) ⚠️ REEMPLAZAR
SENDGRID_API_KEY = (tu-api-key) ⚠️ AGREGAR (si usas emails)
EMAIL_FROM = noreply@tudominio.com ⚠️ AGREGAR (si usas emails)
```

---

## 🎯 Prioridad de Correcciones

### 🔴 URGENTE (Para que funcione):
1. Reemplazar `<tu-project-id>` en GOOGLE_CLOUD_PROJECT (si usas OCR)
2. Configurar GOOGLE_APPLICATION_CREDENTIALS_JSON (mejor que GOOGLE_CREDENTIALS_PATH)
3. Reemplazar placeholders de WhatsApp (si usas WhatsApp)

### 🟡 IMPORTANTE (Recomendado):
4. Agregar IVA_PERCENTAGE = 0.15
5. Eliminar DB_PASSWORD (redundante)

### 🟢 OPCIONAL:
6. Agregar JWT_ACCESS_TOKEN_EXPIRES = 3600
7. Agregar variables de SendGrid (si usas emails)

---

## 📝 Notas Importantes

- **DATABASE_URL**: Ya está correcta ✅
- **SECRET_KEY y JWT_SECRET_KEY**: Ya están configuradas ✅
- **Placeholders**: Deben reemplazarse con valores reales antes de usar esas funcionalidades
- **DB_PASSWORD**: Es redundante, puedes eliminarla
- **GOOGLE_CREDENTIALS_PATH**: No funcionará en Render, mejor usar GOOGLE_APPLICATION_CREDENTIALS_JSON
