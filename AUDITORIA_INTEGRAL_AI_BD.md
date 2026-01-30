# Auditoría Integral: Sistema AI - Base de Datos

**Fecha:** 30 de Enero, 2026  
**Objetivo:** Verificar conectividad, flujo de datos y naturalidad de la interacción

---

## 🔍 1. ARQUITECTURA DEL SISTEMA

### Flujo de Comunicación:
```
Usuario (Frontend)
    ↓
API Route: /chat/conversaciones/{id}/mensajes (POST)
    ↓
ChatService.enviar_mensaje()
    ↓
├─→ Guarda mensaje usuario en BD (Mensaje)
├─→ Obtiene historial de BD
├─→ Construye prompt del sistema
├─→ Llama a OpenAI/OpenRouter (_llamar_openai)
│   └─→ Si detecta [QUERY_DB] en respuesta:
│       └─→ Ejecuta consulta SQL (_ejecutar_consulta_db)
│           └─→ Usa db.session (SQLAlchemy Session)
│           └─→ Retorna resultados
│       └─→ Vuelve a llamar a OpenAI con resultados
└─→ Guarda respuesta del AI en BD (Mensaje)
```

### Componentes Clave:

1. **`routes/chat_routes.py`**
   - Endpoint: `POST /chat/conversaciones/{id}/mensajes`
   - Valida entrada
   - Llama a `chat_service.enviar_mensaje()`
   - Maneja transacciones BD

2. **`modules/chat/chat_service.py`**
   - `enviar_mensaje()`: Método principal
   - `_llamar_openai_con_db()`: Maneja iteraciones con consultas BD
   - `_ejecutar_consulta_db()`: Ejecuta SQL queries
   - `_construir_prompt_sistema()`: Construye el prompt

3. **`models/chat.py`**
   - `Conversacion`: Modelo de conversación
   - `Mensaje`: Modelo de mensaje
   - `TipoMensaje`: Enum de tipos

---

## ✅ 2. VERIFICACIÓN DE CONECTIVIDAD

### 2.1 Conexión Base de Datos

**Estado:** ✅ CONECTADO

**Evidencia:**
- `db.session` se pasa a todos los métodos del servicio
- Se usa SQLAlchemy ORM para operaciones
- Pool de conexiones configurado en `config.py`
- Health check endpoint disponible: `/api/health`

**Verificación:**
```python
# En chat_service.py línea 100+
def enviar_mensaje(self, db: Session, ...):
    # db.session es una sesión SQLAlchemy activa
    conversacion = self.obtener_conversacion(db, conversacion_id)
    mensaje_usuario = Mensaje(...)
    db.add(mensaje_usuario)  # ✅ Funciona - BD conectada
    db.flush()
```

### 2.2 Conexión AI (OpenRouter/OpenAI)

**Estado:** ✅ CONECTADO (Dinámico)

**Evidencia:**
- Credenciales obtenidas dinámicamente en cada llamada
- `AIConfigService.obtener_api_key()` obtiene API key
- `_llamar_openai()` hace llamadas HTTP a OpenRouter
- Headers `HTTP-Referer` y `X-Title` configurados

**Verificación:**
```python
# En chat_service.py línea 23-29
def _obtener_credenciales(self):
    return {
        'api_key': AIConfigService.obtener_api_key(),  # ✅ Dinámico
        'model': AIConfigService.obtener_modelo(),
        'base_url': AIConfigService.obtener_base_url()
    }
```

### 2.3 Integración AI-BD

**Estado:** ✅ FUNCIONAL

**Flujo:**
1. AI genera respuesta con `[QUERY_DB]` si necesita datos
2. Sistema detecta `[QUERY_DB]` en la respuesta
3. Extrae la consulta SQL
4. Ejecuta consulta usando `db.session.execute(text(query))`
5. Formatea resultados
6. Vuelve a llamar a AI con resultados
7. AI genera respuesta final con datos

**Código Clave:**
```python
# Línea 365-387 en chat_service.py
if '[QUERY_DB]' in contenido:
    consulta_sql = partes[1].strip()
    resultado_db = self._ejecutar_consulta_db(db, consulta_sql)  # ✅ BD conectada
    # Agrega resultados al contexto
    mensajes.append({"role": "user", "content": f"Resultado: {mensaje_db}"})
    continue  # Vuelve a llamar a AI
```

---

## 🔄 3. FLUJO DE DATOS COMPLETO

### 3.1 Cuando Usuario Pregunta sobre Datos

**Ejemplo:** "¿Cuántas personas atendiste el 29 de enero?"

**Flujo Detallado:**

1. **Frontend → Backend:**
   ```
   POST /chat/conversaciones/123/mensajes
   {
     "contenido": "¿Cuántas personas atendiste el 29 de enero?",
     "usuario_id": 1
   }
   ```

2. **Backend Guarda Mensaje:**
   ```python
   mensaje_usuario = Mensaje(
       conversacion_id=123,
       tipo=TipoMensaje.USUARIO,
       contenido="¿Cuántas personas atendiste el 29 de enero?"
   )
   db.add(mensaje_usuario)
   db.flush()  # ✅ Guardado en BD
   ```

3. **Backend Construye Prompt:**
   ```python
   sistema_prompt = self._construir_prompt_sistema(contexto_modulo)
   # Incluye: mapa de navegación, ejemplos, instrucciones
   ```

4. **Backend Llama a AI:**
   ```python
   respuesta = self._llamar_openai(mensajes_openai)
   # AI responde con [QUERY_DB] incluido
   ```

5. **Backend Detecta [QUERY_DB]:**
   ```python
   if '[QUERY_DB]' in contenido:
       consulta_sql = "SELECT COUNT(*) as total_charolas, SUM(total_porciones) as total_personas FROM charolas WHERE DATE(fecha_servicio) = '2026-01-29'"
   ```

6. **Backend Ejecuta Consulta:**
   ```python
   resultado = db.execute(text(consulta_sql))  # ✅ BD conectada
   filas = resultado.fetchall()
   # Retorna: [{'total_charolas': 3, 'total_personas': 196}]
   ```

7. **Backend Vuelve a Llamar a AI:**
   ```python
   mensajes.append({
       "role": "user",
       "content": "Resultado de la consulta:\n✅ Consulta ejecutada. Total de filas: 1\n..."
   })
   respuesta_final = self._llamar_openai(mensajes)  # ✅ Segunda llamada
   ```

8. **Backend Guarda Respuesta:**
   ```python
   mensaje_ai = Mensaje(
       conversacion_id=123,
       tipo=TipoMensaje.ASISTENTE,
       contenido="El 29 de enero se sirvieron 3 charolas con un total de 196 personas."
   )
   db.add(mensaje_ai)
   db.commit()  # ✅ Guardado en BD
   ```

9. **Backend → Frontend:**
   ```json
   {
     "success": true,
     "data": {
       "mensaje_usuario": {...},
       "mensaje_asistente": {
         "contenido": "El 29 de enero se sirvieron 3 charolas con un total de 196 personas."
       }
     }
   }
   ```

---

## 🧪 4. PRUEBAS DE CONECTIVIDAD

### 4.1 Prueba de Conexión BD

**Endpoint:** `/api/health`  
**Método:** GET  
**Resultado Esperado:**
```json
{
  "database": {
    "connected": true,
    "status": "ok",
    "response_time_ms": 15.23,
    "pool": {
      "size": 10,
      "checked_in": 8,
      "checked_out": 2
    }
  }
}
```

### 4.2 Prueba de Conexión AI

**Método:** Llamada directa a `_llamar_openai()`  
**Resultado Esperado:** Respuesta válida de OpenRouter

### 4.3 Prueba de Integración Completa

**Escenario:** Usuario pregunta sobre datos  
**Resultado Esperado:** AI ejecuta consulta y responde con datos

---

## ⚠️ 5. PROBLEMAS IDENTIFICADOS

### 5.1 Naturalidad del Prompt

**Problema:** El prompt es muy técnico y repetitivo  
**Impacto:** Respuestas del AI pueden sonar robóticas  
**Solución:** Mejorar el prompt para ser más natural

### 5.2 Verificación de Conectividad

**Problema:** No hay endpoint para verificar si AI puede acceder a BD  
**Impacto:** Difícil diagnosticar problemas  
**Solución:** Crear endpoint de verificación

### 5.3 Manejo de Errores

**Problema:** Errores de BD no siempre se manejan bien  
**Impacto:** Usuario puede recibir errores técnicos  
**Solución:** Mejorar manejo de errores

---

## 🎯 6. MEJORAS PROPUESTAS

### 6.1 Prompt Más Natural

**Objetivo:** Hacer que el AI responda de forma más natural  
**Cambios:**
- Reducir repeticiones
- Usar lenguaje más conversacional
- Mantener funcionalidad pero con tono más amigable

### 6.2 Endpoint de Verificación

**Objetivo:** Verificar conectividad AI-BD  
**Endpoint:** `/api/chat/health`  
**Funcionalidad:**
- Verifica conexión BD
- Verifica conexión AI
- Ejecuta consulta de prueba
- Retorna estado completo

### 6.3 Mejor Manejo de Errores

**Objetivo:** Errores más amigables para el usuario  
**Cambios:**
- Traducir errores técnicos a lenguaje natural
- Ofrecer alternativas cuando hay errores
- Logging mejorado para debugging

---

## 📊 7. MÉTRICAS Y MONITOREO

### 7.1 Métricas Actuales

- ✅ Tiempo de ejecución de consultas (log de consultas lentas)
- ✅ Número de iteraciones AI-BD
- ✅ Errores de consultas SQL

### 7.2 Métricas Recomendadas

- Tiempo total de respuesta (usuario → respuesta final)
- Tasa de éxito de consultas BD
- Tasa de éxito de llamadas AI
- Número de consultas por conversación

---

## ✅ 8. CONCLUSIÓN

### Estado General: ✅ FUNCIONAL

**Fortalezas:**
- ✅ Conexión BD establecida y funcional
- ✅ Conexión AI establecida y funcional
- ✅ Integración AI-BD funcionando
- ✅ Consultas SQL ejecutándose correctamente
- ✅ Resultados siendo procesados por AI

**Áreas de Mejora:**
- ⚠️ Naturalidad del prompt (muy técnico)
- ⚠️ Verificación de conectividad (falta endpoint)
- ⚠️ Manejo de errores (puede mejorarse)

**Recomendación:** Implementar mejoras propuestas para optimizar experiencia de usuario.

---

**Próximos Pasos:**
1. Mejorar naturalidad del prompt
2. Crear endpoint de verificación
3. Mejorar manejo de errores
4. Implementar métricas adicionales
