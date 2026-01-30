# Verificación de Conectividad AI-BD

**Endpoint:** `GET /api/chat/health`  
**Propósito:** Verificar que el sistema AI puede acceder a la base de datos

---

## 📋 Respuesta del Endpoint

### Ejemplo de Respuesta Exitosa:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "database": {
      "connected": true,
      "status": "ok",
      "response_time_ms": 15.23,
      "pool": {
        "size": 10,
        "checked_in": 8,
        "checked_out": 2,
        "overflow": 0,
        "invalid": 0
      }
    },
    "ai": {
      "configured": true,
      "model": "openai/gpt-4o-mini",
      "base_url": "configured"
    },
    "integration": {
      "status": "ok",
      "bd_conectada": true,
      "ai_configurado": true,
      "mensaje": "Sistema AI-BD operativo"
    },
    "test_query": {
      "ejecutada": true,
      "tiempo_ms": 12.45,
      "status": "ok"
    }
  }
}
```

### Ejemplo de Respuesta con Error:

```json
{
  "success": false,
  "error": "Problemas de conectividad detectados",
  "code": "CONNECTIVITY_ERROR",
  "data": {
    "status": "error",
    "database": {
      "connected": false,
      "status": "error",
      "message": "Connection timeout"
    },
    "ai": {
      "configured": false,
      "model": null,
      "base_url": "not_configured"
    },
    "integration": {
      "status": "error",
      "bd_conectada": false,
      "ai_configurado": false,
      "mensaje": "Problemas de conectividad detectados"
    }
  }
}
```

---

## 🔍 Qué Verifica

1. **Conexión a Base de Datos:**
   - Verifica que la conexión esté activa
   - Mide tiempo de respuesta
   - Muestra estadísticas del pool de conexiones

2. **Configuración AI:**
   - Verifica que la API key esté configurada
   - Verifica que el modelo esté configurado
   - Verifica que la base URL esté configurada

3. **Integración AI-BD:**
   - Verifica que ambos sistemas estén operativos
   - Confirma que el AI puede acceder a BD

4. **Consulta de Prueba:**
   - Ejecuta una consulta simple de prueba
   - Mide el tiempo de ejecución
   - Verifica que las consultas funcionen

---

## 🧪 Cómo Usar

### Desde el Navegador:
```
GET https://kohde-demo-1.onrender.com/api/chat/health
```

### Desde cURL:
```bash
curl https://kohde-demo-1.onrender.com/api/chat/health
```

### Desde el Frontend:
```javascript
fetch('/api/chat/health')
  .then(res => res.json())
  .then(data => {
    if (data.success && data.data.status === 'ok') {
      console.log('✅ Sistema AI-BD operativo');
      console.log('BD:', data.data.database.connected);
      console.log('AI:', data.data.ai.configured);
    } else {
      console.error('❌ Problemas de conectividad');
    }
  });
```

---

## ✅ Interpretación de Resultados

### Sistema Operativo:
- `status: "ok"`
- `database.connected: true`
- `ai.configured: true`
- `integration.status: "ok"`

### Problemas Detectados:

1. **BD No Conectada:**
   - `database.connected: false`
   - Verificar configuración de DATABASE_URL
   - Verificar que PostgreSQL esté corriendo

2. **AI No Configurado:**
   - `ai.configured: false`
   - Verificar que OPENROUTER_API_KEY esté configurada
   - Verificar configuración en Render

3. **Consulta de Prueba Fallida:**
   - `test_query.ejecutada: false`
   - Verificar permisos de la BD
   - Verificar que las tablas existan

---

## 🔄 Monitoreo Continuo

Este endpoint puede usarse para:
- Health checks automáticos
- Monitoreo de disponibilidad
- Diagnóstico de problemas
- Verificación post-despliegue

---

**Estado:** ✅ Endpoint implementado y listo para usar
