# 🔧 Configurar VITE_API_URL en Render

## 🎯 Problema

El frontend está intentando conectarse a `http://localhost:5000` en lugar de la URL del backend en producción, causando errores de conexión.

## ✅ Solución

Necesitas configurar la variable de entorno `VITE_API_URL` en el Web Service del frontend en Render.

---

## 📋 Pasos para Configurar en Render

### Paso 1: URL del Backend

La URL del backend es: `https://kohde-demo-ewhi.onrender.com/api`

### Paso 2: Configurar Variable en el Frontend

1. Ve al servicio del frontend: `kohde-demo-1` (o `kfronend-demo`)
2. Haz clic en **"Environment"** en el menú lateral
3. Haz clic en **"Add Environment Variable"**
4. Configura:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://kohde-demo-ewhi.onrender.com/api`
5. Haz clic en **"Save Changes"**

### Paso 3: Redesplegar el Frontend

1. Después de guardar la variable, Render automáticamente iniciará un nuevo despliegue
2. Espera a que termine el build y deploy
3. Verifica que el frontend ahora se conecta correctamente al backend

---

## 🔍 Verificar la Configuración

### Opción 1: Verificar en los Logs

Después del despliegue, revisa los logs del frontend. Deberías ver que el build incluye la variable `VITE_API_URL`.

### Opción 2: Verificar en el Navegador

1. Abre la aplicación en el navegador
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña **Network**
4. Verifica que las peticiones van a la URL del backend (no a `localhost:5000`)

---

## ⚠️ Notas Importantes

1. **Variables VITE**: Las variables que empiezan con `VITE_` son expuestas al código del frontend durante el build. Por eso necesitas configurarlas antes del build.

2. **Formato de la URL**: 
   - ✅ Correcto: `https://erp-restaurantes.onrender.com/api`
   - ❌ Incorrecto: `https://erp-restaurantes.onrender.com/api/` (sin trailing slash)

3. **Re-build necesario**: Si cambias la variable después del build, necesitas hacer un nuevo build. Render lo hace automáticamente cuando guardas la variable.

---

## 🐛 Troubleshooting

### Si sigue usando localhost:

1. Verifica que la variable se llama exactamente `VITE_API_URL` (mayúsculas)
2. Verifica que el valor es correcto (con `/api` al final)
3. Verifica que el servicio se redesplegó después de agregar la variable
4. Limpia la caché del navegador (Ctrl+Shift+R)

### Si obtienes errores CORS:

1. Verifica que el backend tiene configurada la URL del frontend en `CORS_ORIGINS`
2. El backend debe permitir requests desde `https://kohde-demo-1.onrender.com`

---

## 📝 Ejemplo de Configuración Correcta

```
Variable: VITE_API_URL
Value: https://kohde-demo-ewhi.onrender.com/api
```

Después de configurar esto, el frontend usará automáticamente esta URL en lugar de `localhost:5000`.
