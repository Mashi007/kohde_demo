# Configuración de URLs en Render

## 🌐 URLs de tus Servicios

- **Backend (Web Service)**: `https://kohde-demo-ewhi.onrender.com`
- **Frontend (Static Site)**: `https://kfronend-demo.onrender.com`

---

## 📍 Dónde Configurar Cada URL

### 1. **Variable de Entorno en Static Site (Frontend)**

**Ubicación**: Static Site → Environment Variables

**Variable a agregar**:
```
VITE_API_URL = https://kohde-demo-ewhi.onrender.com/api
```

**Cómo agregar**:
1. Ve a tu Static Site `kfronend-demo` en Render
2. Sección **"Environment"**
3. Click en **"Add Environment Variable"**
4. Nombre: `VITE_API_URL`
5. Valor: `https://kohde-demo-ewhi.onrender.com/api`
6. Click en **"Save Changes"**

---

### 2. **CORS en Web Service (Backend)**

**Ubicación**: Ya está configurado en `app.py`

El código ya tiene configurado CORS para permitir requests desde:
- `https://kfronend-demo.onrender.com` (tu frontend)
- `http://localhost:3000` (desarrollo local)

**No necesitas hacer nada adicional**, pero si quieres verificar:

1. Ve a tu Web Service `kohde-demo-ewhi` en Render
2. Verifica que el código esté desplegado con la última versión
3. El CORS ya está configurado automáticamente

---

### 3. **Para Desarrollo Local**

Crea un archivo `frontend/.env` (no versionar):

```env
VITE_API_URL=http://localhost:5000/api
```

O si tu backend local corre en otro puerto:
```env
VITE_API_URL=http://localhost:5000/api
```

---

## ✅ Checklist de Configuración

### Static Site (Frontend):
- [ ] Variable `VITE_API_URL` agregada con valor: `https://kohde-demo-ewhi.onrender.com/api`
- [ ] Build Command: `npm install && npm run build`
- [ ] Publish Directory: `dist`
- [ ] Root Directory: `frontend`

### Web Service (Backend):
- [ ] CORS configurado para permitir `https://kfronend-demo.onrender.com`
- [ ] PostgreSQL conectado en "Connections"
- [ ] Variables de entorno configuradas (SECRET_KEY, JWT_SECRET_KEY, etc.)

---

## 🔗 URLs Finales

### Backend API:
```
https://kohde-demo-ewhi.onrender.com/api
```

### Endpoints disponibles:
- `https://kohde-demo-ewhi.onrender.com/api/crm/clientes`
- `https://kohde-demo-ewhi.onrender.com/api/contabilidad/facturas`
- `https://kohde-demo-ewhi.onrender.com/api/logistica/inventario`
- etc.

### Frontend:
```
https://kfronend-demo.onrender.com
```

---

## 🧪 Probar la Conexión

1. Abre tu frontend: `https://kfronend-demo.onrender.com`
2. Abre la consola del navegador (F12)
3. Ve a la pestaña "Network"
4. Deberías ver requests a: `https://kohde-demo-ewhi.onrender.com/api/...`

Si ves errores de CORS, verifica que:
- La variable `VITE_API_URL` esté correctamente configurada
- El backend tenga CORS habilitado (ya está configurado)
- Ambos servicios estén desplegados y activos

---

## 📝 Notas Importantes

- **Backend URL**: Siempre termina en `/api` porque todas las rutas tienen ese prefijo
- **Frontend URL**: No necesita `/api` al final
- **CORS**: Ya está configurado en el código, no necesitas hacer nada adicional
- **Variables de entorno**: Se aplican después de hacer "Save Changes" y el servicio se reinicia automáticamente

---

¡Listo! Con esto deberías tener todo conectado. 🚀
