# Variables de Entorno Faltantes - Verificación Completa
**Fecha:** 30 de Enero, 2026  
**Servicio:** `kohde_demo` (Backend)

---

## 🔍 Variables Faltantes Identificadas

Después de revisar el código (`config.py` y `app.py`), se identificaron variables que **NO aparecieron en las imágenes** pero que son **usadas en el código**:

---

## 🔴 Variables Críticas Faltantes

### 1. **CORS_ORIGINS** ⚠️ IMPORTANTE
**Ubicación en código:** `app.py` línea 42-44

```python
cors_origins = os.getenv('CORS_ORIGINS', 
    'https://kohde-demo-1.onrender.com,https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173'
).split(',')
```

**Estado:** ⚠️ **NO VISIBLE en las imágenes**

**Valor por defecto:** 
```
https://kohde-demo-1.onrender.com,https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173
```

**Impacto:**
- ✅ Si no está configurada, usa el valor por defecto (funciona)
- ⚠️ Si el frontend cambia de URL, podría causar problemas de CORS
- ⚠️ El valor por defecto incluye `kfronend-demo.onrender.com` pero el frontend real es `kohde-demo-1.onrender.com`

**Recomendación:** 
- Verificar si está configurada en Render
- Si no está, agregarla con el valor correcto:
  ```
  CORS_ORIGINS=https://kohde-demo-1.onrender.com,http://localhost:3000,http://localhost:5173
  ```

---

### 2. **IVA_PERCENTAGE** ⚠️ IMPORTANTE
**Ubicación en código:** `config.py` línea 118

```python
IVA_PERCENTAGE = float(os.getenv('IVA_PERCENTAGE', '0.15'))  # 15% IVA por defecto
```

**Estado:** ⚠️ **NO VISIBLE en las imágenes**

**Valor por defecto:** `0.15` (15%)

**Impacto:**
- ✅ Si no está configurada, usa 15% (funciona)
- ⚠️ Si el país/región requiere un IVA diferente, debe configurarse

**Recomendación:**
- Verificar si está configurada en Render
- Si no está y el IVA es diferente a 15%, agregarla

---

## 🟡 Variables Importantes Faltantes

### 3. **ENABLE_SCHEDULER** ⚠️
**Ubicación en código:** `app.py` línea 129

```python
if os.getenv('ENABLE_SCHEDULER', 'true').lower() == 'true':
```

**Estado:** ⚠️ **NO VISIBLE en las imágenes**

**Valor por defecto:** `'true'` (habilitado)

**Impacto:**
- ✅ Si no está configurada, las tareas programadas están habilitadas (funciona)
- ⚠️ Si se necesita deshabilitar temporalmente, debe configurarse

**Recomendación:**
- Verificar si está configurada en Render
- Si no está, puede agregarse como `ENABLE_SCHEDULER=true` (o `false` para deshabilitar)

---

### 4. **ENVIRONMENT** ⚠️
**Ubicación en código:** `app.py` línea 128

```python
is_production = os.getenv('ENVIRONMENT', '').lower() == 'production' or not Config.DEBUG
```

**Estado:** ⚠️ **NO VISIBLE en las imágenes**

**Valor por defecto:** `''` (vacío)

**Impacto:**
- ✅ Si no está configurada, se detecta producción por `DEBUG=False` (funciona)
- ⚠️ Podría ser útil para logging o comportamiento específico

**Recomendación:**
- Opcional: Agregar `ENVIRONMENT=production` para claridad

---

## 🟢 Variables Opcionales Faltantes

### 5. **Variables de Email** ⚠️
**Ubicación en código:** `config.py` líneas 82-93

| Variable | Valor por Defecto | Estado |
|----------|-------------------|--------|
| `EMAIL_PROVIDER` | `'sendgrid'` | ⚠️ No visible |
| `SENDGRID_API_KEY` | `''` | ⚠️ No visible |
| `GMAIL_SMTP_USER` | `''` | ⚠️ No visible |
| `GMAIL_SMTP_PASSWORD` | `''` | ⚠️ No visible |
| `EMAIL_FROM` | `'noreply@restaurantes.com'` | ⚠️ No visible |
| `EMAIL_NOTIFICACIONES_PEDIDOS` | `'a3b7x9q@gmail.com'` | ⚠️ No visible |

**Impacto:**
- ⚠️ Si se usan notificaciones por email, estas variables son **REQUERIDAS**
- ✅ Si no se usan, pueden quedar sin configurar

**Recomendación:**
- Si se usan notificaciones por email, verificar y configurar según el proveedor:
  - **SendGrid:** `EMAIL_PROVIDER=sendgrid` + `SENDGRID_API_KEY=...`
  - **Gmail:** `EMAIL_PROVIDER=gmail` + `GMAIL_SMTP_USER=...` + `GMAIL_SMTP_PASSWORD=...`

---

### 6. **Variables de Pool de Conexiones BD** ⚠️
**Ubicación en código:** `config.py` líneas 48-57

| Variable | Valor por Defecto | Estado |
|----------|-------------------|--------|
| `DB_POOL_SIZE` | `10` | ⚠️ No visible |
| `DB_POOL_RECYCLE` | `3600` | ⚠️ No visible |
| `DB_POOL_PRE_PING` | `'true'` | ⚠️ No visible |
| `DB_MAX_OVERFLOW` | `20` | ⚠️ No visible |
| `DB_POOL_TIMEOUT` | `30` | ⚠️ No visible |
| `DB_CONNECT_TIMEOUT` | `10` | ⚠️ No visible |

**Impacto:**
- ✅ Valores por defecto son adecuados para la mayoría de casos
- ⚠️ Solo necesarias si se requiere ajuste fino del pool de conexiones

**Recomendación:**
- Opcional: Solo configurar si hay problemas de conexión o se necesita optimización

---

### 7. **OPENAI_API_KEY** ⚠️
**Ubicación en código:** `config.py` línea 97

```python
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
```

**Estado:** ⚠️ **NO VISIBLE en las imágenes**

**Impacto:**
- ✅ Si `OPENROUTER_API_KEY` está configurada, puede no ser necesaria
- ⚠️ Algunos módulos podrían requerirla directamente

**Recomendación:**
- Verificar si está configurada
- Si se usa OpenRouter exclusivamente, puede no ser necesaria

---

### 8. **Variables de Google Cloud Adicionales** ⚠️
**Ubicación en código:** `config.py` líneas 65-68

| Variable | Valor por Defecto | Estado |
|----------|-------------------|--------|
| `GOOGLE_CREDENTIALS_PATH` | `''` | ⚠️ No visible |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | `''` | ⚠️ No visible |

**Impacto:**
- ✅ Si se usa Workload Identity (como parece ser el caso), estas no son necesarias
- ⚠️ Solo necesarias si se usan credenciales JSON manuales

**Recomendación:**
- No necesarias si Workload Identity está configurado (como parece ser)

---

## 📊 Resumen de Variables Faltantes

### 🔴 Críticas (Deben Verificarse):
1. ✅ `CORS_ORIGINS` - Importante para CORS
2. ✅ `IVA_PERCENTAGE` - Importante para cálculos de facturas

### 🟡 Importantes (Recomendadas):
3. ⚠️ `ENABLE_SCHEDULER` - Para tareas programadas
4. ⚠️ `ENVIRONMENT` - Para detección de entorno

### 🟢 Opcionales (Solo si se usan):
5. ⚠️ Variables de Email (si se usan notificaciones)
6. ⚠️ Variables de Pool de BD (solo para optimización)
7. ⚠️ `OPENAI_API_KEY` (si no se usa solo OpenRouter)
8. ⚠️ Variables adicionales de Google Cloud (si no se usa Workload Identity)

---

## ✅ Acciones Recomendadas

### Prioridad Alta:

1. **Verificar CORS_ORIGINS:**
   ```bash
   # En Render Dashboard → Environment Variables
   # Verificar si existe CORS_ORIGINS
   # Si no existe, agregar:
   CORS_ORIGINS=https://kohde-demo-1.onrender.com,http://localhost:3000,http://localhost:5173
   ```

2. **Verificar IVA_PERCENTAGE:**
   ```bash
   # En Render Dashboard → Environment Variables
   # Verificar si existe IVA_PERCENTAGE
   # Si no existe y el IVA es diferente a 15%, agregar:
   IVA_PERCENTAGE=0.15  # o el valor correcto para tu país
   ```

### Prioridad Media:

3. **Verificar Variables de Email (si se usan):**
   ```bash
   # Si se usan notificaciones por email:
   EMAIL_PROVIDER=sendgrid  # o 'gmail'
   SENDGRID_API_KEY=...  # si usa SendGrid
   # o
   GMAIL_SMTP_USER=...  # si usa Gmail
   GMAIL_SMTP_PASSWORD=...  # si usa Gmail
   EMAIL_NOTIFICACIONES_PEDIDOS=tu-email@gmail.com
   ```

### Prioridad Baja:

4. **Variables Opcionales:**
   - `ENABLE_SCHEDULER=true` (ya está habilitado por defecto)
   - `ENVIRONMENT=production` (opcional, se detecta por DEBUG)
   - Variables de pool de BD (solo si hay problemas)

---

## 🔍 Cómo Verificar en Render

1. **Ir a Render Dashboard:**
   - https://dashboard.render.com
   - Seleccionar servicio `kohde_demo`

2. **Ir a Environment Variables:**
   - Settings → Environment
   - Revisar todas las variables listadas

3. **Verificar Variables Faltantes:**
   - Buscar cada variable de la lista
   - Si no existe, agregarla con el valor apropiado

---

## 📝 Notas Importantes

### Variables con Valores por Defecto:
- ✅ Si una variable tiene valor por defecto en el código, **NO es crítica** si falta
- ⚠️ Sin embargo, es **recomendable** configurarlas explícitamente para claridad

### Variables Condicionales:
- ⚠️ Algunas variables solo son necesarias si se usa cierta funcionalidad
- ✅ Ejemplo: Variables de email solo si se usan notificaciones por email

### Variables Automáticas de Render:
- ✅ `DATABASE_URL` - Automática cuando se conecta PostgreSQL
- ✅ `RENDER_SERVICE_ID` - Automática
- ✅ `PORT` - Automática

---

## ✅ Conclusión

**Variables que DEBEN verificarse:**
1. 🔴 `CORS_ORIGINS` - Importante para CORS
2. 🔴 `IVA_PERCENTAGE` - Importante para cálculos

**Variables RECOMENDADAS:**
3. 🟡 Variables de Email (si se usan notificaciones)
4. 🟡 `ENABLE_SCHEDULER` (para claridad)

**Variables OPCIONALES:**
5. 🟢 Resto de variables (solo si se necesitan ajustes específicos)

---

**Verificación realizada por:** Sistema de Auditoría Automatizada  
**Próxima acción:** Verificar en Render Dashboard las variables faltantes
