# 🚨 SOLUCIÓN: Token de OpenRouter Expuesto

## ⚠️ PROBLEMA CRÍTICO

Tu token de OpenRouter fue expuesto en un repositorio público de GitHub y ha sido **deshabilitado automáticamente** por seguridad.

**Token afectado**: `...45cc` (termina en 45cc)
**Ubicación encontrada**: `scripts/configurar_openrouter.py`

## ✅ ACCIONES INMEDIATAS REQUERIDAS

### 1. Crear un Nuevo Token de OpenRouter

1. Ve a **https://openrouter.ai/keys**
2. Inicia sesión con tu cuenta
3. Haz clic en **"Create Key"** o **"Nueva Key"**
4. Copia el nuevo token (comienza con `sk-or-v1-`)

### 2. Actualizar en Render.com

1. Ve a **Render Dashboard** → Tu servicio → **Environment**
2. Busca la variable `OPENROUTER_API_KEY`
3. Reemplaza el valor con tu **nuevo token**
4. Guarda los cambios
5. Reinicia el servicio (o espera el despliegue automático)

### 3. Limpiar Archivos Locales

Los siguientes archivos han sido actualizados para **NO** contener tokens hardcodeados:

- ✅ `scripts/configurar_openrouter.py` - Actualizado
- ⚠️ `scripts/agregar_variables_openrouter.py` - Necesita revisión
- ⚠️ Archivos de documentación - Contienen ejemplos (no crítico)

**Archivos que DEBES revisar manualmente:**

```bash
# Buscar cualquier referencia al token antiguo
grep -r "9b5b48bc1d48536d7277b77be9e9449e97dd9a8bce7361f27cab20cd105045cc" .
```

### 4. Verificar que .gitignore Proteja Archivos Sensibles

Asegúrate de que `.gitignore` incluya:

```
.env
.env.local
*.backup
```

## 📋 PASOS DETALLADOS

### Paso 1: Generar Nuevo Token

```
1. Abre https://openrouter.ai/keys
2. Inicia sesión
3. Crea un nuevo token
4. Copia el token completo
```

### Paso 2: Actualizar Render.com

```
1. Render Dashboard → Tu servicio
2. Environment → Editar OPENROUTER_API_KEY
3. Pegar nuevo token
4. Guardar
5. Reiniciar servicio
```

### Paso 3: Verificar Funcionamiento

```bash
# Ejecutar diagnóstico
python scripts/diagnostico_error_401.py
```

O prueba directamente en:
- https://kohde-demo-1.onrender.com/chat

## 🔒 MEJORES PRÁCTICAS DE SEGURIDAD

### ✅ HACER:
- ✅ Usar variables de entorno para tokens
- ✅ Agregar `.env` a `.gitignore`
- ✅ Nunca hacer commit de tokens en código
- ✅ Usar secretos de GitHub Actions si es necesario
- ✅ Rotar tokens periódicamente

### ❌ NO HACER:
- ❌ Hardcodear tokens en archivos de código
- ❌ Subir `.env` al repositorio
- ❌ Compartir tokens en documentación pública
- ❌ Usar el mismo token en múltiples proyectos

## 📝 ARCHIVOS ACTUALIZADOS

1. **scripts/configurar_openrouter.py**
   - ✅ Eliminado token hardcodeado
   - ✅ Ahora lee de variables de entorno
   - ✅ Solicita token si no está disponible

2. **Archivos pendientes de limpieza:**
   - `scripts/agregar_variables_openrouter.py` - Contiene token en línea 10
   - Archivos de documentación (no crítico, son ejemplos)

## 🧪 VERIFICACIÓN POST-CORRECCIÓN

Después de actualizar el token:

1. **Verificar en Render.com:**
   ```
   OPENROUTER_API_KEY=sk-or-v1-[NUEVO-TOKEN]
   ```

2. **Ejecutar diagnóstico:**
   ```bash
   python scripts/diagnostico_error_401.py
   ```

3. **Probar el chat:**
   - Ve a https://kohde-demo-1.onrender.com/chat
   - Envía un mensaje de prueba
   - Deberías recibir respuesta del AI

## ⚠️ NOTA IMPORTANTE

El token anterior (`...45cc`) está **permanentemente deshabilitado** y no puede ser reactivado. Debes crear uno nuevo.

## 📞 SOPORTE

Si tienes problemas:
1. Verifica que el nuevo token sea correcto
2. Verifica que tenga créditos en OpenRouter
3. Revisa los logs de Render para errores específicos
4. Ejecuta el script de diagnóstico

## ✅ CHECKLIST DE CORRECCIÓN

- [ ] Crear nuevo token en OpenRouter
- [ ] Actualizar `OPENROUTER_API_KEY` en Render.com
- [ ] Reiniciar servicio en Render
- [ ] Verificar que el chat funcione
- [ ] Limpiar referencias al token antiguo en código local
- [ ] Verificar que `.gitignore` proteja archivos sensibles
