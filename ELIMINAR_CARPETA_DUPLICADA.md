# Instrucciones para Eliminar Carpeta Duplicada

## 🔍 Situación Detectada

Hay una carpeta `kohde_demo/` dentro del repositorio que es una **duplicación completa** de todos los archivos que ya están en la raíz.

## ✅ Solución

### Paso 1: Verificar que el .gitignore está actualizado
El archivo `.gitignore` ya tiene `kohde_demo/` agregado.

### Paso 2: Eliminar la carpeta duplicada

**Desde PowerShell o CMD, ejecuta:**

```powershell
cd C:\Users\PORTATIL\Documents\GitHub\kohde_demo
Remove-Item -Recurse -Force kohde_demo
```

**O desde el Explorador de Windows:**
1. Ve a `C:\Users\PORTATIL\Documents\GitHub\kohde_demo`
2. Haz clic derecho en la carpeta `kohde_demo`
3. Selecciona "Eliminar"
4. Confirma la eliminación

### Paso 3: Verificar que Git ya no la detecta

```powershell
git status
```

Deberías ver: `nothing to commit, working tree clean`

## ⚠️ Importante

- **NO elimines** los archivos de la raíz (app.py, config.py, frontend/, etc.)
- **SÍ elimina** solo la carpeta `kohde_demo/` que está dentro del repositorio
- Todos los archivos importantes ya están en la raíz y están commiteados

## 📁 Estructura Correcta

```
C:\Users\PORTATIL\Documents\GitHub\kohde_demo\
├── app.py
├── config.py
├── frontend/
├── models/
├── modules/
├── routes/
├── utils/
├── migrations/
├── requirements.txt
├── README.md
└── .gitignore
```

**NO debe haber** una carpeta `kohde_demo/` dentro.
