# ✅ Configuración Correcta de Render - Static Site

## 📋 Entendiendo el Prefijo Visual de Render

Cuando configuras `Root Directory: frontend`, Render muestra un prefijo visual `frontend/ $` en los campos. **Esto es NORMAL y está bien**.

Render está mostrando cómo se verá el comando cuando se ejecute, pero **NO necesitas escribir ese prefijo**.

---

## ✅ Configuración Correcta

### Opción 1: Con Root Directory = `frontend` (Recomendado)

```
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

**Render mostrará visualmente**:
- `frontend/ $ npm install && npm run build` (pero tú escribes solo `npm install && npm run build`)
- `frontend/ $ dist` (pero tú escribes solo `dist`)

**Cómo funciona**:
- Render cambia a `frontend/` antes de ejecutar
- Ejecuta `npm install && npm run build` desde `frontend/`
- Busca `dist` dentro de `frontend/` → `frontend/dist`

---

### Opción 2: Sin Root Directory (Alternativa)

Si prefieres NO usar Root Directory:

```
Root Directory: (vacío)
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/dist
```

**Cómo funciona**:
- Render ejecuta desde la raíz del repositorio
- El comando `cd frontend` cambia al directorio
- Busca `frontend/dist` desde la raíz

---

## 🎯 Recomendación

**Usa la Opción 1** (con Root Directory):
- Más limpio
- Render maneja el cambio de directorio automáticamente
- Los comandos son más simples

**Los valores que debes escribir** (ignorando el prefijo visual):
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

---

## ✅ Verificación

Si Render muestra:
```
Root Directory: frontend
Build Command: frontend/ $ npm install && npm run build
Publish Directory: frontend/ $ dist
```

**Está CORRECTO**. El `frontend/ $` es solo visual.

Lo importante es que:
- ✅ Root Directory = `frontend`
- ✅ Build Command contiene `npm install && npm run build` (sin el prefijo al escribirlo)
- ✅ Publish Directory contiene `dist` (sin el prefijo al escribirlo)

---

## 🔍 Cómo Verificar que Funciona

Después del deploy, verifica los logs:
1. Ve a Static Site → Logs
2. Deberías ver algo como:
   ```
   Running: npm install && npm run build
   Building from: frontend/
   Publishing: frontend/dist
   ```

Si ves errores como "package.json not found", entonces el Root Directory no está configurado correctamente.

---

## 📝 Resumen

- **El prefijo `frontend/ $` es solo visual** - Render lo muestra para indicar que los comandos se ejecutarán desde `frontend/`
- **Escribe los comandos normalmente** sin incluir el prefijo
- **Si Render no te deja borrar el prefijo**, está bien - es solo visual
- **Lo importante**: Root Directory = `frontend`, Build Command tiene `npm install && npm run build`, Publish Directory tiene `dist`
