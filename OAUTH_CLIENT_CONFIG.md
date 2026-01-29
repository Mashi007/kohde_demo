# 🔐 Configuración de Cliente OAuth en Google Cloud

## ⚠️ Importante: ¿Realmente Necesitas Esto?

### Para Cloud Vision API (OCR):
**NO necesitas crear un cliente OAuth**. Solo necesitas:
- ✅ Cuenta de servicio
- ✅ Clave JSON de la cuenta de servicio
- ✅ API habilitada

### Para WhatsApp Business API:
**NO necesitas OAuth de Google Cloud**. WhatsApp usa tokens de Meta, no OAuth de Google.

---

## 📋 Si Realmente Necesitas OAuth (Para Otra Integración)

### Configuración del Cliente OAuth:

**Tipo de aplicación**: `Aplicación web` ✅ (ya está seleccionado)

**Nombre**: `Cliente web c-Whatspp` ✅ (o el que prefieras)

### Orígenes autorizados de JavaScript:
**NO necesitas agregar nada** si solo usas Cloud Vision API desde el backend.

Si necesitas usar desde el frontend, agrega:
```
https://kfronend-demo.onrender.com
```

### URIs de redireccionamiento autorizados:
**NO necesitas agregar nada** para Cloud Vision API.

Si necesitas OAuth para otra cosa, agrega:
```
https://kohde-demo-ewhi.onrender.com/api/auth/callback
```

---

## ✅ Recomendación: CANCELAR Este Paso

**Para tu ERP con Cloud Vision API**, NO necesitas crear un cliente OAuth.

**Lo que SÍ necesitas**:
1. ✅ Cuenta de servicio (ya la estás creando)
2. ✅ Permisos en la cuenta de servicio
3. ✅ Clave JSON de la cuenta de servicio
4. ✅ Cloud Vision API habilitada

---

## 🎯 Qué Hacer Ahora

### Opción 1: Cancelar OAuth (Recomendado)
1. Haz clic en **"Cancelar"**
2. Ve a **IAM y administración** → **Cuentas de servicio**
3. Busca tu cuenta `cobranzas-what`
4. Ve a la pestaña **"Claves"**
5. Genera una clave **JSON** (no OAuth)

### Opción 2: Si Realmente Necesitas OAuth
1. Deja los campos vacíos (no necesitas URIs para Cloud Vision)
2. Haz clic en **"Crear"**
3. Luego genera la clave JSON de la cuenta de servicio

---

## 📝 Resumen

**Para Cloud Vision API**:
- ❌ NO necesitas cliente OAuth
- ✅ SÍ necesitas cuenta de servicio con clave JSON
- ✅ SÍ necesitas Cloud Vision API habilitada

**Para WhatsApp**:
- ❌ NO necesitas OAuth de Google
- ✅ SÍ necesitas tokens de Meta (Facebook)

---

## 🔧 Siguiente Paso Correcto

1. **Cancela** la creación del cliente OAuth
2. Ve a **Cuentas de servicio** → `cobranzas-what`
3. Genera una **clave JSON** (no OAuth)
4. Usa esa clave JSON en Render con `GOOGLE_APPLICATION_CREDENTIALS_JSON`

¿Quieres que te guíe para generar la clave JSON correcta?
