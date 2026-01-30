# Guía de Ejecución de Scripts de Mock Data

## 📍 Ubicación

Abre una terminal (PowerShell o CMD) en el directorio raíz del proyecto:
```
c:\Users\PORTATIL\Documents\GitHub\kohde_demo
```

## 🚀 Comando Básico

```bash
python scripts/nombre_del_script.py
```

## 📋 Orden Recomendado de Ejecución

### Paso 1: Datos Base (Requisitos Previos)

```bash
# 1. Items (crea proveedores automáticamente si no existen)
python scripts/init_items.py

# 2. Facturas (requiere items y proveedores)
python scripts/init_facturas.py

# 3. Recetas (requiere items)
python scripts/init_recetas.py
```

### Paso 2: Módulos de Logística (10 ejemplos cada uno)

```bash
# 4. Pedidos de Compra (requiere items y proveedores)
python scripts/init_pedidos.py

# 5. Pedidos Internos (requiere items)
python scripts/init_pedidos_internos.py

# 6. Requerimientos (requiere items)
python scripts/init_requerimientos.py

# 7. Mermas (requiere items)
python scripts/init_mermas.py

# 8. Charolas (requiere items, recomendado recetas)
python scripts/init_charolas.py

# 9. Costos Estandarizados (requiere items, recomendado facturas)
python scripts/init_costos.py
```

## ✅ Ejemplo de Ejecución Completa

```powershell
# Navegar al directorio del proyecto (si no estás ahí)
cd c:\Users\PORTATIL\Documents\GitHub\kohde_demo

# Verificar que estás en el directorio correcto
ls scripts

# Ejecutar scripts uno por uno
python scripts/init_items.py
python scripts/init_facturas.py
python scripts/init_recetas.py
python scripts/init_pedidos.py
python scripts/init_pedidos_internos.py
python scripts/init_requerimientos.py
python scripts/init_mermas.py
python scripts/init_charolas.py
python scripts/init_costos.py
```

## 🔍 Verificación

Cada script mostrará:
- ✓ Mensajes de éxito cuando crea datos
- ↻ Mensajes cuando los datos ya existen
- ❌ Mensajes de error si faltan requisitos previos

## ⚠️ Notas Importantes

1. **Los scripts son idempotentes**: Puedes ejecutarlos múltiples veces sin duplicar datos
2. **Verificación automática**: Cada script verifica si los datos ya existen antes de crearlos
3. **Dependencias**: Si un script falla por falta de datos, ejecuta primero los scripts de requisitos previos
4. **Base de datos**: Asegúrate de que tu base de datos PostgreSQL esté corriendo y configurada en `.env`

## 🐛 Solución de Problemas

### Error: "No hay items activos"
```bash
# Ejecuta primero:
python scripts/init_items.py
```

### Error: "No hay proveedores activos"
```bash
# Los proveedores se crean automáticamente con init_items.py
python scripts/init_items.py
```

### Error: "No module named 'app'"
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd c:\Users\PORTATIL\Documents\GitHub\kohde_demo
python scripts/init_items.py
```

### Error de conexión a base de datos
```bash
# Verifica que PostgreSQL esté corriendo
# Verifica tu archivo .env tiene DATABASE_URL configurado
```
