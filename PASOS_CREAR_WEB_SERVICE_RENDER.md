# 📋 Pasos Detallados: Crear Web Service y Eliminar Static Site en Render

## 🎯 Objetivo
Convertir el servicio `kfronend-demo` de Static Site a Web Service para que las rutas SPA funcionen correctamente.

---

## 📝 PASO 1: Crear el Nuevo Web Service

### 1.1. Ir al Dashboard de Render
1. Abre tu navegador y ve a: https://dashboard.render.com
2. Inicia sesión con tu cuenta

### 1.2. Crear Nuevo Web Service
1. En el dashboard principal, haz clic en el botón **"New +"** (arriba a la derecha)
2. Selecciona **"Web Service"** de la lista de opciones

### 1.3. Conectar el Repositorio
1. Si ya tienes repositorios conectados:
   - Selecciona el repositorio que contiene tu proyecto (`kohde_demo` o el nombre que tengas)
2. Si no tienes repositorios conectados:
   - Haz clic en **"Connect account"** para conectar GitHub/GitLab/Bitbucket
   - Selecciona tu repositorio

### 1.4. Configurar el Web Service

Completa los siguientes campos:

#### **Name**
```
kfronend-demo
```
(O el nombre que prefieras, puede ser diferente al anterior)

#### **Environment**
Selecciona: **Node**

#### **Region**
Selecciona la región más cercana (ej: `Oregon (US West)`)

#### **Branch**
```
main
```
(O la rama que uses: `master`, `develop`, etc.)

#### **Root Directory** (Opcional pero Recomendado)
```
frontend
```
Esto le dice a Render que todos los comandos se ejecutarán desde la carpeta `frontend/`

#### **Build Command**
Si usaste Root Directory = `frontend`:
```
npm install && npm run build
```

Si NO usaste Root Directory (dejaste vacío):
```
cd frontend && npm install && npm run build
```

#### **Start Command**
Si usaste Root Directory = `frontend`:
```
node server.js
```

Si NO usaste Root Directory:
```
cd frontend && node server.js
```

#### **Instance Type**
Selecciona: **Free** (o el plan que prefieras)

### 1.5. Configurar Variables de Entorno

Haz clic en **"Advanced"** → **"Add Environment Variable"** y agrega:

| Key | Value |
|-----|-------|
| `NODE_VERSION` | `18.x` |

**NOTA**: La variable `PORT` NO es necesaria - Render la asigna automáticamente.

### 1.6. Crear el Servicio
1. Revisa toda la configuración
2. Haz clic en **"Create Web Service"**
3. Render comenzará a construir y desplegar automáticamente

---

## ⏳ PASO 2: Esperar el Despliegue

1. Render mostrará los logs del build en tiempo real
2. Espera a que termine el proceso (puede tomar 2-5 minutos)
3. Verifica que el estado sea **"Live"** (debe aparecer un indicador verde)

### Verificar que Funcionó:
1. Haz clic en la URL del servicio (ej: `https://kfronend-demo.onrender.com`)
2. Debe cargar tu aplicación React
3. Navega a `/recetas` y **refresca la página** - NO debe dar 404

---

## 🗑️ PASO 3: Eliminar el Static Site Antiguo

### 3.1. Ir al Static Site Antiguo
1. En el dashboard de Render, busca el servicio antiguo `kfronend-demo` (el que es Static Site)
2. Haz clic en él para abrirlo

### 3.2. Eliminar el Servicio
1. Ve a la pestaña **"Settings"** (Configuración)
2. Desplázate hasta el final de la página
3. Busca la sección **"Danger Zone"** o **"Delete Service"**
4. Haz clic en **"Delete"** o **"Delete Service"**
5. Render te pedirá confirmación:
   - Escribe el nombre del servicio para confirmar: `kfronend-demo`
   - Haz clic en **"Delete"** o **"Confirm Delete"**

### 3.3. Confirmación
- El servicio será eliminado permanentemente
- Los logs y configuración se perderán (pero ya tienes el nuevo Web Service funcionando)

---

## ✅ PASO 4: Verificación Final

### 4.1. Verificar Tipo de Servicio
1. Ve al nuevo servicio `kfronend-demo` (Web Service)
2. Ve a **Settings**
3. Verifica que diga **"Web Service"** (no Static Site)
4. Verifica que el **Start Command** sea `node server.js` (o `cd frontend && node server.js`)

### 4.2. Verificar Logs
1. Ve a la pestaña **"Logs"**
2. Deberías ver algo como:
   ```
   === SERVIDOR EXPRESS INICIANDO ===
   ✓ Puerto: 10000
   ✓ Host: 0.0.0.0
   ✓ Directorio dist: /opt/render/project/src/frontend/dist
   ✓ Listo para recibir requests
   ```

### 4.3. Probar Rutas SPA
1. Accede a: `https://[tu-url].onrender.com/`
2. Debe cargar la aplicación
3. Navega a diferentes rutas:
   - `/recetas` → Refresca → ✅ Debe funcionar
   - `/items` → Refresca → ✅ Debe funcionar
   - `/facturas` → Refresca → ✅ Debe funcionar
4. Todas las rutas deben funcionar al refrescar (no dar 404)

---

## 🔧 Configuración Recomendada (Resumen)

```
Name: kfronend-demo
Environment: Node
Root Directory: frontend
Build Command: npm install && npm run build
Start Command: node server.js
Instance Type: Free

Environment Variables:
- NODE_VERSION: 18.x
```

---

## 🚨 Solución de Problemas

### Problema: El build falla
**Solución**: 
- Verifica que `package.json` existe en `frontend/`
- Verifica que `server.js` existe en `frontend/`
- Revisa los logs de build para ver el error específico

### Problema: El servicio no inicia
**Solución**:
- Verifica que el Start Command sea correcto
- Verifica los logs del servicio
- Asegúrate de que `dist` se haya creado después del build

### Problema: Sigue dando 404 al refrescar
**Solución**:
- Verifica que sea Web Service (no Static Site)
- Verifica los logs - debe aparecer `[SPA] Sirviendo index.html`
- Verifica que `server.js` esté funcionando correctamente

### Problema: No puedo eliminar el Static Site
**Solución**:
- Asegúrate de tener permisos de administrador
- Verifica que no haya dependencias o servicios relacionados
- Si es necesario, contacta al soporte de Render

---

## 📚 Notas Adicionales

- **URL**: La URL del nuevo servicio puede ser diferente si cambiaste el nombre
- **Variables de Entorno**: Si tenías variables en el Static Site, cópialas al Web Service
- **Dominio Personalizado**: Si tenías un dominio personalizado, reconéctalo al nuevo Web Service
- **Costo**: El plan Free tiene limitaciones, pero es suficiente para desarrollo

---

## ✅ Checklist Final

- [ ] Web Service creado y desplegado
- [ ] Estado del servicio es "Live"
- [ ] La aplicación carga correctamente en la raíz `/`
- [ ] Las rutas SPA funcionan al refrescar (no dan 404)
- [ ] Static Site antiguo eliminado
- [ ] Logs muestran que Express está funcionando
- [ ] Variables de entorno configuradas correctamente

---

¡Listo! Tu aplicación ahora debería funcionar correctamente con rutas SPA en Render. 🎉
