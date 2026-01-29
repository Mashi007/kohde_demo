# 🔧 Correcciones Necesarias en Render

## ❌ Problemas Detectados

### 1. **Static Site - Variable de Entorno INCORRECTA** ⚠️ CRÍTICO

**Problema**: 
```
VITE_API_URL = https://kfronend-demo.onrender.com
```
Esto apunta al frontend (incorrecto).

**Corrección**:
```
VITE_API_URL = https://kohde-demo-ewhi.onrender.com/api
```
Debe apuntar al **backend** con `/api` al final.

**Cómo corregir**:
1. Ve a Static Site `kfronend-demo` → **Environment**
2. Busca la variable `VITE_API_URL`
3. Haz clic en **Edit** (lápiz)
4. Cambia el valor a: `https://kohde-demo-ewhi.onrender.com/api`
5. Guarda los cambios

---

### 2. **Static Site - Root Directory VACÍO** ⚠️ IMPORTANTE

**Problema**: 
```
Root Directory: (vacío)
```

**Corrección**:
```
Root Directory: frontend
```

**Cómo corregir**:
1. Ve a Static Site `kfronend-demo` → **Settings** → **Build & Deploy**
2. Busca **Root Directory**
3. Haz clic en **Edit**
4. Ingresa: `frontend`
5. Guarda los cambios

**Por qué es importante**: 
- Render necesita saber que el código del frontend está en la carpeta `frontend/`
- Sin esto, el build fallará porque buscará `package.json` en la raíz

---

### 3. **Static Site - Build Command** (Opcional mejorar)

**Actual**:
```
npm install && npm run build
```

**Mejor opción** (si configuras Root Directory):
```
npm install && npm run build
```
Con Root Directory = `frontend`, este comando se ejecutará desde `frontend/`

**Alternativa** (si NO usas Root Directory):
```
cd frontend && npm install && npm run build
```

---

### 4. **Web Service - Tipo "Node"** ⚠️ INCORRECTO

**Problema**: 
El Web Service muestra "Node" pero debería ser "Python"

**Cómo verificar/corregir**:
1. Ve a Web Service `kohde-demo-ewhi` → **Settings**
2. Verifica que:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

Si dice "Node", necesitas cambiar el tipo de servicio o recrearlo como Python.

---

## ✅ Configuración Correcta Final

### Static Site (`kfronend-demo`):

```
Name: kfronend-demo
Repository: https://github.com/Mashi007/kohde_demo
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
Auto-Deploy: On Commit

Environment Variables:
  VITE_API_URL = https://kohde-demo-ewhi.onrender.com/api
```

### Web Service (`kohde-demo-ewhi`):

```
Name: kohde-demo-ewhi
Environment: Python 3
Repository: https://github.com/Mashi007/kohde_demo
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
Auto-Deploy: On Commit

Environment Variables:
  DATABASE_URL = (automático desde PostgreSQL)
  SECRET_KEY = (tu clave)
  JWT_SECRET_KEY = (tu clave)
  DEBUG = false
  STOCK_MINIMUM_THRESHOLD_PERCENTAGE = 0.2
  IVA_PERCENTAGE = 0.15
  (y otras variables según necesites)
```

---

## 🎯 Prioridad de Correcciones

1. **URGENTE**: Corregir `VITE_API_URL` (apunta al backend incorrecto)
2. **IMPORTANTE**: Agregar `Root Directory: frontend`
3. **VERIFICAR**: Que Web Service sea Python, no Node

---

## 🧪 Después de Corregir

1. Guarda todos los cambios
2. Render reiniciará automáticamente los servicios
3. Espera a que termine el deploy
4. Prueba el frontend: `https://kfronend-demo.onrender.com`
5. Abre la consola del navegador (F12) → Network
6. Deberías ver requests a: `https://kohde-demo-ewhi.onrender.com/api/...`

---

## 📝 Notas

- **VITE_API_URL**: Debe apuntar al **backend**, no al frontend
- **Root Directory**: Necesario porque el código está en `frontend/`
- **Build Command**: Se ejecuta desde Root Directory si está configurado
- **CORS**: Ya está configurado en el código del backend
