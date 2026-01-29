# 📱 Módulo de Configuración WhatsApp

## 📋 Descripción

Módulo completo para configurar WhatsApp Business API y capturar imágenes/documentos para procesamiento con OCR.

---

## 🚀 Funcionalidades

### 1. **Verificación de Configuración**
Verifica que todas las variables de entorno de WhatsApp estén configuradas.

### 2. **Prueba de Conexión**
Prueba la conexión con WhatsApp API y obtiene información del número de teléfono.

### 3. **Descarga de Imágenes**
Descarga automáticamente imágenes y documentos recibidos por WhatsApp.

### 4. **Procesamiento de Facturas**
Procesa imágenes de facturas usando OCR y crea registros en el sistema.

### 5. **Envío de Mensajes de Prueba**
Envía mensajes de prueba para verificar la configuración.

---

## 🔌 Endpoints API

### Verificar Configuración
```http
GET /api/configuracion/whatsapp/verificar
```

**Respuesta:**
```json
{
  "api_url": "https://graph.facebook.com/v18.0",
  "access_token": "✅ Configurado",
  "phone_number_id": "123456789",
  "verify_token": "✅ Configurado",
  "webhook_url": "https://graph.facebook.com/v18.0/webhook",
  "completo": true
}
```

---

### Probar Conexión
```http
POST /api/configuracion/whatsapp/probar
```

**Respuesta:**
```json
{
  "exito": true,
  "mensaje": "Conexión exitosa",
  "datos": {
    "display_phone_number": "+593999999999",
    "quality_rating": "GREEN"
  }
}
```

---

### Información del Webhook
```http
GET /api/configuracion/whatsapp/webhook-info
```

**Respuesta:**
```json
{
  "configurado": true,
  "apps": [
    {
      "id": "app_id",
      "name": "app_name"
    }
  ]
}
```

---

### Enviar Mensaje de Prueba
```http
POST /api/configuracion/whatsapp/enviar-prueba
Content-Type: application/json

{
  "numero_destino": "593999999999"
}
```

**Respuesta:**
```json
{
  "exito": true,
  "mensaje": "Mensaje enviado correctamente",
  "whatsapp_id": "wamid.xxx"
}
```

---

### Procesar Imagen Manualmente
```http
POST /api/configuracion/whatsapp/procesar-imagen
Content-Type: application/json

{
  "media_id": "123456789",
  "sender_id": "593999999999",
  "tipo": "factura"
}
```

**Respuesta:**
```json
{
  "exito": true,
  "mensaje": "Factura procesada correctamente",
  "factura_id": 1,
  "numero_factura": "001-001-0001234",
  "total": 150.50
}
```

---

## 🔧 Variables de Entorno Requeridas

```bash
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=tu_access_token
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id
WHATSAPP_VERIFY_TOKEN=tu_verify_token_personalizado
```

---

## 📥 Webhook de WhatsApp

### URL del Webhook
```
https://tu-dominio.com/whatsapp/webhook
```

### Verificación (GET)
WhatsApp enviará una petición GET para verificar el webhook:
- `hub.mode`: debe ser "subscribe"
- `hub.verify_token`: debe coincidir con `WHATSAPP_VERIFY_TOKEN`
- `hub.challenge`: código que debes devolver

### Recepción de Mensajes (POST)
El webhook recibe automáticamente:
- **Imágenes**: Se procesan como facturas con OCR
- **Documentos**: Se procesan como facturas con OCR
- **Texto**: Se puede procesar comandos (futuro)

---

## 🖼️ Flujo de Captura de Imágenes

1. **Usuario envía imagen por WhatsApp**
   - El webhook recibe la notificación
   - Se extrae el `media_id` de la imagen

2. **Descarga de la Imagen**
   - Se obtiene la URL temporal de la imagen desde WhatsApp API
   - Se descarga la imagen al servidor
   - Se guarda en `uploads/facturas/`

3. **Procesamiento con OCR**
   - Se usa Google Cloud Vision API para extraer texto
   - Se parsean los datos de la factura
   - Se crea el registro en la base de datos

4. **Confirmación al Usuario**
   - Se envía un mensaje de confirmación por WhatsApp
   - Se incluye número de factura y total

---

## 📝 Ejemplo de Uso

### Desde el Frontend

```javascript
// Verificar configuración
const verificar = async () => {
  const response = await fetch('/api/configuracion/whatsapp/verificar');
  const config = await response.json();
  console.log(config);
};

// Probar conexión
const probar = async () => {
  const response = await fetch('/api/configuracion/whatsapp/probar', {
    method: 'POST'
  });
  const resultado = await response.json();
  console.log(resultado);
};

// Enviar mensaje de prueba
const enviarPrueba = async (numero) => {
  const response = await fetch('/api/configuracion/whatsapp/enviar-prueba', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ numero_destino: numero })
  });
  const resultado = await response.json();
  console.log(resultado);
};
```

---

## 🔍 Estructura del Módulo

```
modules/
  configuracion/
    __init__.py
    whatsapp.py          # Servicio de configuración WhatsApp

routes/
  configuracion_routes.py  # Endpoints API de configuración
  whatsapp_webhook.py      # Webhook para recibir mensajes
```

---

## ✅ Checklist de Configuración

- [ ] Variables de entorno configuradas en Render
- [ ] Webhook configurado en Meta Business Suite
- [ ] URL del webhook verificada
- [ ] Token de verificación configurado
- [ ] Probar conexión con `/api/configuracion/whatsapp/probar`
- [ ] Enviar mensaje de prueba
- [ ] Probar envío de imagen por WhatsApp

---

## 🐛 Solución de Problemas

### Error: "WhatsApp no configurado correctamente"
- Verifica que todas las variables de entorno estén configuradas
- Usa `/api/configuracion/whatsapp/verificar` para ver qué falta

### Error: "Error de conexión"
- Verifica que el `WHATSAPP_ACCESS_TOKEN` sea válido
- Verifica que el `WHATSAPP_PHONE_NUMBER_ID` sea correcto
- Revisa los logs del servidor

### Las imágenes no se descargan
- Verifica que el `WHATSAPP_ACCESS_TOKEN` tenga permisos de lectura de medios
- Revisa que el directorio `uploads/facturas/` exista y tenga permisos de escritura

---

## 📚 Referencias

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Webhook Setup Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)

---

¡El módulo está listo para usar! 🎉
