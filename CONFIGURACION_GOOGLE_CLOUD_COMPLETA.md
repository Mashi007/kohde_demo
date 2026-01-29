# 🔧 Configuración Completa de Google Cloud Vision

## ✅ Paso 1: Crear Cuenta de Servicio (Ya lo estás haciendo)

**Configuración actual**:
- Nombre: `Cobranzas_what` ✅
- ID: `cobranzas-what` ✅
- Email: `cobranzas-what@cobranzas-485720.iam.gserviceaccount.com` ✅

**Siguiente**: Haz clic en **"Crear y continuar"**

---

## 📋 Paso 2: Asignar Permisos (IMPORTANTE)

Después de crear la cuenta, en el paso **"2 Permisos (opcional)"**:

### Permisos Necesarios:

1. **Cloud Vision API User** (Recomendado)
   - Permite usar la API de Vision
   - Busca: `Cloud Vision API User`
   - Selecciónalo y haz clic en "Agregar"

2. **O alternativamente**:
   - **Editor** (más permisos, pero funciona)
   - **Cloud Vision API Service Agent** (si está disponible)

**Haz clic en "Continuar"** después de agregar los permisos.

---

## 🔑 Paso 3: Generar Clave JSON

1. **Después de crear la cuenta**, ve a:
   - IAM y administración → Cuentas de servicio
   - Busca `cobranzas-what@cobranzas-485720.iam.gserviceaccount.com`
   - Haz clic en la cuenta

2. **Ve a la pestaña "Claves"**

3. **Haz clic en "Agregar clave"** → **"Crear nueva clave"**

4. **Selecciona "JSON"**

5. **Haz clic en "Crear"**
   - Se descargará un archivo JSON
   - **Guárdalo seguro** (no lo subas a Git)

---

## 🚀 Paso 4: Habilitar Cloud Vision API

1. **Ve a "APIs y servicios"** → **"Biblioteca"**

2. **Busca "Cloud Vision API"**

3. **Haz clic en "Habilitar"**

4. **Espera** a que se habilite (puede tomar unos minutos)

---

## 📝 Paso 5: Configurar en Render

### Variables a Configurar:

1. **GOOGLE_CLOUD_PROJECT**:
   ```
   KEY: GOOGLE_CLOUD_PROJECT
   VALUE: cobranzas-485720
   ```
   (Tu Project ID que veo en la imagen)

2. **GOOGLE_APPLICATION_CREDENTIALS_JSON**:
   ```
   KEY: GOOGLE_APPLICATION_CREDENTIALS_JSON
   VALUE: (pega TODO el contenido del JSON descargado en UNA SOLA LÍNEA)
   ```

3. **Eliminar** (si existe):
   ```
   GOOGLE_CREDENTIALS_PATH ❌
   ```

---

## ✅ Checklist Completo

### En Google Cloud:
- [ ] Cuenta de servicio creada: `cobranzas-what`
- [ ] Permisos asignados: `Cloud Vision API User` o `Editor`
- [ ] Clave JSON generada y descargada
- [ ] Cloud Vision API habilitada

### En Render:
- [ ] `GOOGLE_CLOUD_PROJECT` = `cobranzas-485720`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS_JSON` = (contenido del JSON)
- [ ] `GOOGLE_CREDENTIALS_PATH` eliminada (si existía)

---

## 🎯 Siguiente Acción Inmediata

**Ahora mismo**:
1. Completa la creación de la cuenta de servicio
2. En el paso 2, agrega el permiso **"Cloud Vision API User"**
3. Haz clic en "Listo" o "Continuar"
4. Luego genera la clave JSON

---

## 📋 Resumen de lo que Necesitas

1. ✅ **Project ID**: `cobranzas-485720` (ya lo tienes)
2. ⏳ **Cuenta de servicio**: `cobranzas-what` (en proceso)
3. ⏳ **Permisos**: Agregar "Cloud Vision API User"
4. ⏳ **Clave JSON**: Generar después de crear la cuenta
5. ⏳ **Habilitar API**: Cloud Vision API
6. ⏳ **Configurar en Render**: Variables de entorno

---

¿Necesitas ayuda con algún paso específico después de crear la cuenta de servicio?
