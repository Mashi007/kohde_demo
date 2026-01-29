# Comandos Git para Ejecutar

## 📋 Pasos para hacer commit

Ejecuta estos comandos en PowerShell desde la raíz del repositorio:

```powershell
# 1. Ir a la raíz del repositorio
cd C:\Users\PORTATIL\Documents\GitHub\kohde_demo

# 2. Verificar estado
git status

# 3. Agregar el .gitignore actualizado
git add .gitignore

# 4. Hacer commit
git commit -m "chore: Actualizar .gitignore para ignorar carpeta kohde_demo duplicada"

# 5. Push a GitHub
git push origin main

# 6. Verificar que todo está limpio
git status
```

## ✅ Resultado Esperado

Después de ejecutar estos comandos, deberías ver:
- `nothing to commit, working tree clean` (si ya eliminaste la carpeta kohde_demo)
- O solo el cambio en `.gitignore` si la carpeta aún existe

## 🔧 Si la carpeta kohde_demo aún existe

Si Git todavía detecta la carpeta `kohde_demo/` después del commit, elimínala físicamente:

```powershell
Remove-Item -Recurse -Force kohde_demo
```

Luego verifica:
```powershell
git status
```

Debería mostrar `nothing to commit, working tree clean`.
