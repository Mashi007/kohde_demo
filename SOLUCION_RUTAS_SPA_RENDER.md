# 🔧 Solución: Error 404 al Refrescar Rutas SPA en Render

## 🎯 Problema

Cuando refrescas una ruta como `/recetas` en Render, obtienes un error 404. Esto ocurre porque el servicio está configurado como **Static Site** en lugar de **Web Service**.

## ✅ Solución

### Paso 1: Verificar el Tipo de Servicio en Render

1. Ve al dashboard de Render: https://dashboard.render.com
2. Selecciona el servicio `kfronend-demo`
3. Ve a la pestaña **Settings**
4. Verifica el tipo de servicio en la parte superior

### Paso 2: Cambiar de Static Site a Web Service

Si el servicio está configurado como **Static Site**:

1. **NO puedes convertir directamente** un Static Site a Web Service en Render
2. Tienes dos opciones:

#### Opción A: Crear Nuevo Web Service (Recomendado)

1. Ve a **Dashboard** → **New** → **Web Service**
2. Conecta el mismo repositorio
3. Configura:
   - **Name**: `kfronend-demo` (o el nombre que prefieras)
   - **Environment**: `Node`
   - **Root Directory**: `frontend` (opcional, o déjalo vacío)
   - **Build Command**: 
     ```
     npm install && npm run build
     ```
     O si no usas Root Directory:
     ```
     cd frontend && npm install && npm run build
     ```
   - **Start Command**: 
     ```
     node server.js
     ```
     O si no usas Root Directory:
     ```
     cd frontend && node server.js
     ```
   - **Environment Variables**:
     - `NODE_VERSION`: `18.x`
     - `PORT`: (Render lo asigna automáticamente)

4. Guarda y despliega
5. Una vez que funcione, elimina el Static Site anterior

#### Opción B: Usar render.yaml (Automático)

Si tienes `render.yaml` configurado correctamente (como está ahora):

1. Elimina el servicio Static Site actual en Render
2. Ve a **Dashboard** → **New** → **Blueprint**
3. Conecta tu repositorio
4. Render leerá el `render.yaml` y creará el servicio como **Web Service** automáticamente

### Paso 3: Verificar la Configuración

Después de crear el Web Service, verifica:

1. **Settings** → Debe decir **Web Service** (no Static Site)
2. **Settings** → **Start Command** debe ser `node server.js` (o `cd frontend && node server.js`)
3. **Settings** → NO debe tener campo **Publish Directory** (ese campo solo existe en Static Site)

### Paso 4: Verificar los Logs

Después del despliegue, revisa los logs:

1. Ve a **Logs** en el servicio
2. Deberías ver:
   ```
   === SERVIDOR EXPRESS INICIANDO ===
   ✓ Puerto: [número]
   ✓ Host: 0.0.0.0
   ✓ Directorio dist: [ruta]
   ✓ Listo para recibir requests
   ```

3. Cuando accedas a `/recetas`, deberías ver en los logs:
   ```
   [REQUEST] GET /recetas
   [SPA] Sirviendo index.html para: GET /recetas
   [✓] index.html servido correctamente para: /recetas
   ```

## 🔍 Diferencias Clave

### Static Site
- ❌ Render maneja el routing directamente
- ❌ No ejecuta tu servidor Express
- ❌ No puede manejar rutas SPA al refrescar
- ✅ Tiene campo **Publish Directory**
- ✅ Más simple pero limitado

### Web Service
- ✅ Ejecuta tu servidor Express
- ✅ Puede manejar rutas SPA correctamente
- ✅ Tienes control total sobre el routing
- ❌ NO tiene campo **Publish Directory**
- ✅ Más flexible y potente

## 📝 Configuración Actual en render.yaml

El `render.yaml` ya está configurado correctamente como Web Service:

```yaml
- type: web  # ← Esto es Web Service, NO Static Site
  name: kfronend-demo
  env: node
  buildCommand: cd frontend && npm install && npm run build
  startCommand: cd frontend && node server.js
```

## ✅ Verificación Final

Para verificar que todo funciona:

1. Accede a la raíz: `https://kfronend-demo.onrender.com/`
2. Debe cargar la aplicación
3. Navega a `/recetas` desde la aplicación (debe funcionar)
4. **Refresca la página** en `/recetas` (debe funcionar, no dar 404)
5. Prueba otras rutas como `/items`, `/facturas`, etc.

## 🚨 Si Sigue Sin Funcionar

Si después de cambiar a Web Service sigue dando 404:

1. Verifica los logs del servicio en Render
2. Busca errores relacionados con:
   - `dist` no encontrado
   - `index.html` no encontrado
   - Errores de Node.js
3. Verifica que el build se completó correctamente
4. Verifica que `server.js` existe en `frontend/`

## 📚 Referencias

- [Render Web Services](https://render.com/docs/web-services)
- [Render Static Sites](https://render.com/docs/static-sites)
- [SPA Routing en Render](https://render.com/docs/deploy-create-react-app)
