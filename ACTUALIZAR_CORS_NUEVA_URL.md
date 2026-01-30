# 🔧 Actualizar CORS para Nueva URL del Frontend

## ✅ Cambio Aplicado en el Código

He actualizado `app.py` para incluir la nueva URL del frontend en la configuración de CORS por defecto.

**Antes:**
```python
'https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173'
```

**Ahora:**
```python
'https://kohde-demo-1.onrender.com,https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173'
```

---

## 📋 Pasos Adicionales en Render

### Opción 1: Si NO tienes variable `CORS_ORIGINS` en Render

**No necesitas hacer nada más.** El código ya tiene la nueva URL como valor por defecto.

Solo necesitas:
1. Hacer commit y push de los cambios
2. Render desplegará automáticamente el backend con la nueva configuración

---

### Opción 2: Si SÍ tienes variable `CORS_ORIGINS` en Render

Si configuraste la variable de entorno `CORS_ORIGINS` en el servicio del backend en Render, debes actualizarla:

#### Pasos:

1. Ve al dashboard de Render: https://dashboard.render.com
2. Selecciona el servicio del **backend** (`erp-restaurantes` o el nombre que tenga)
3. Ve a la pestaña **"Environment"** o **"Environment Variables"**
4. Busca la variable `CORS_ORIGINS`
5. Haz clic en ella para editarla
6. Actualiza el valor para incluir la nueva URL:

**Valor actual (ejemplo):**
```
https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173
```

**Valor nuevo:**
```
https://kohde-demo-1.onrender.com,https://kfronend-demo.onrender.com,http://localhost:3000,http://localhost:5173
```

7. Guarda los cambios
8. Render reiniciará automáticamente el servicio con la nueva configuración

---

## 🔍 Cómo Verificar si Tienes la Variable

1. Ve al servicio del backend en Render
2. Ve a **"Environment"** o **"Environment Variables"**
3. Busca `CORS_ORIGINS` en la lista
4. Si existe → Actualízala (Opción 2)
5. Si NO existe → No hagas nada (Opción 1)

---

## ✅ Verificación Final

Después de actualizar:

1. Espera a que Render termine de desplegar/reiniciar
2. Abre el frontend: `https://kohde-demo-1.onrender.com`
3. Intenta hacer login o cualquier acción que requiera comunicación con el backend
4. Abre la consola del navegador (F12)
5. Verifica que NO haya errores de CORS como:
   - `Access to XMLHttpRequest blocked by CORS policy`
   - `No 'Access-Control-Allow-Origin' header`

Si no hay errores de CORS, ¡todo está funcionando correctamente! ✅

---

## 📝 Notas

- **Mantuve la URL antigua** (`kfronend-demo`) en la lista por si acaso aún la necesitas durante la transición
- **Puedes eliminar la URL antigua** después de verificar que todo funciona con la nueva
- **Las URLs de desarrollo** (`localhost:3000` y `localhost:5173`) se mantienen para desarrollo local

---

## 🚨 Si Sigue Habiendo Errores de CORS

1. Verifica que el backend se haya desplegado correctamente
2. Revisa los logs del backend en Render
3. Verifica que la variable `CORS_ORIGINS` tenga el formato correcto (URLs separadas por comas, sin espacios extra)
4. Asegúrate de que la URL del frontend sea exactamente: `https://kohde-demo-1.onrender.com` (sin `/` al final)
