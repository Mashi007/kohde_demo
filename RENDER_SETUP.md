# Guía de Configuración en Render

## 📋 Pasos para Desplegar en Render

### 1. Crear PostgreSQL Database

1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Postgres"**
3. Configura:
   - **Name**: `erp-restaurantes-db`
   - **Database**: `erp_restaurantes`
   - **User**: `erp_user` (o el que prefieras)
   - **Plan**: `Free` (para pruebas) o `Starter` (para producción)
4. Haz clic en **"Create Database"**
5. **IMPORTANTE**: Guarda la **Internal Database URL** que Render te proporciona

### 2. Crear Web Service

1. En el dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio de GitHub/GitLab
4. Configura:
   - **Name**: `erp-restaurantes`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: `Free` (para pruebas) o `Starter` (para producción)

### 3. Configurar Variables de Entorno

En la sección **"Environment"** del Web Service, agrega:

#### Base de Datos (Automático si conectas PostgreSQL)
- `DATABASE_URL` - Render la proporciona automáticamente cuando conectas el servicio PostgreSQL
  - O manualmente: `postgresql://usuario:password@host:5432/erp_restaurantes`

#### Flask
- `SECRET_KEY` - Genera una clave segura (puedes usar: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `JWT_SECRET_KEY` - Otra clave segura
- `DEBUG` - `false` (en producción)

#### Google Cloud Vision (OCR)
- `GOOGLE_CLOUD_PROJECT` - Tu project ID de Google Cloud
- `GOOGLE_CREDENTIALS_PATH` - Ruta al archivo JSON (o mejor, codifica el JSON en una variable)
- O mejor aún, usa: `GOOGLE_APPLICATION_CREDENTIALS_JSON` con el contenido del JSON codificado

#### WhatsApp Business API
- `WHATSAPP_ACCESS_TOKEN` - Token de acceso de Meta
- `WHATSAPP_PHONE_NUMBER_ID` - ID del número de teléfono
- `WHATSAPP_VERIFY_TOKEN` - Token personalizado para verificar webhook

#### SendGrid (Opcional)
- `SENDGRID_API_KEY` - API Key de SendGrid
- `EMAIL_FROM` - Email remitente

#### Configuración
- `STOCK_MINIMUM_THRESHOLD_PERCENTAGE` - `0.2` (20%)
- `IVA_PERCENTAGE` - `0.15` (15%)

### 4. Conectar PostgreSQL al Web Service

1. En la configuración del **Web Service**
2. Ve a la sección **"Connections"**
3. Haz clic en **"Connect"** junto al servicio PostgreSQL que creaste
4. Render automáticamente agregará `DATABASE_URL` a las variables de entorno

### 5. Ejecutar Migraciones

Después del primer despliegue, necesitas ejecutar el schema SQL:

**Opción 1: Desde Render Shell**
1. Ve a tu Web Service en Render
2. Haz clic en **"Shell"**
3. Ejecuta:
```bash
psql $DATABASE_URL -f migrations/initial_schema.sql
```

**Opción 2: Desde tu máquina local**
1. Obtén la **External Database URL** de Render
2. Ejecuta:
```bash
psql "postgresql://usuario:password@host:5432/erp_restaurantes" -f migrations/initial_schema.sql
```

**Opción 3: Usar Python (Recomendado)**
El código ya tiene `db.create_all()` en `app.py`, que creará las tablas automáticamente en el primer despliegue.

### 6. Configurar Webhook de WhatsApp

1. Obtén la URL de tu Web Service: `https://tu-app.onrender.com`
2. Ve a [Meta for Developers](https://developers.facebook.com/)
3. Configura el webhook:
   - **Callback URL**: `https://tu-app.onrender.com/whatsapp/webhook`
   - **Verify Token**: El mismo que configuraste en `WHATSAPP_VERIFY_TOKEN`
   - **Subscription Fields**: `messages`

## 🔧 Solución de Problemas

### Error de conexión a PostgreSQL
- Verifica que el servicio PostgreSQL esté corriendo
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que el Web Service esté conectado al PostgreSQL en "Connections"

### Error al crear tablas
- Verifica los logs del Web Service en Render
- Asegúrate de que `db.create_all()` se ejecute correctamente
- Si es necesario, ejecuta el schema SQL manualmente

### Webhook de WhatsApp no funciona
- Verifica que la URL sea HTTPS (Render lo proporciona automáticamente)
- Verifica que el `WHATSAPP_VERIFY_TOKEN` coincida
- Revisa los logs del Web Service para ver errores

## 📝 Notas Importantes

- **Free Plan**: Los servicios se "duermen" después de 15 minutos de inactividad
- **Starter Plan**: Los servicios están siempre activos
- **Base de datos**: El plan Free tiene límites de almacenamiento (1GB)
- **Variables sensibles**: Nunca las subas a Git, úsalas solo en Render

## ✅ Checklist de Despliegue

- [ ] PostgreSQL creado y conectado
- [ ] Web Service creado y conectado al repositorio
- [ ] Variables de entorno configuradas
- [ ] PostgreSQL conectado al Web Service en "Connections"
- [ ] Schema SQL ejecutado (o `db.create_all()` funcionó)
- [ ] Webhook de WhatsApp configurado
- [ ] Aplicación funcionando correctamente

---

¡Listo! Tu ERP debería estar funcionando en Render. 🚀
