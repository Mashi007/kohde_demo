# Instrucciones para Migrar con DBeaver

## 📋 Archivos SQL Creados

1. **`migracion_indices_y_enums.sql`** - Script principal de migración
2. **`rollback_migracion.sql`** - Script para revertir cambios (si es necesario)

---

## 🚀 Pasos para Ejecutar la Migración en DBeaver

### Paso 1: Conectar a la Base de Datos

1. Abre **DBeaver**
2. Crea una nueva conexión PostgreSQL (si no existe):
   - Click derecho en "Database Navigator" → "New" → "Database Connection"
   - Selecciona **PostgreSQL**
   - Configura la conexión con los datos de Render:
     - **Host:** (obtener de DATABASE_URL en Render)
     - **Port:** (obtener de DATABASE_URL en Render)
     - **Database:** (obtener de DATABASE_URL en Render)
     - **Username:** (obtener de DATABASE_URL en Render)
     - **Password:** (obtener de DATABASE_URL en Render)
   - Click en "Test Connection" para verificar
   - Click en "Finish"

### Paso 2: Abrir el Script SQL

1. En DBeaver, ve a **File** → **Open SQL Script**
2. Selecciona el archivo **`migracion_indices_y_enums.sql`**
3. El script se abrirá en el editor SQL

### Paso 3: Revisar el Script (Opcional pero Recomendado)

- Lee el script completo para entender qué hará
- Verifica que las tablas mencionadas existen en tu base de datos
- Asegúrate de tener permisos suficientes

### Paso 4: Hacer Backup (MUY IMPORTANTE)

**Antes de ejecutar la migración, haz un backup:**

1. Click derecho en tu base de datos → **Tools** → **Backup Database**
2. Selecciona:
   - **Format:** Plain SQL
   - **File:** (elige una ubicación segura)
   - Click en **Start**
3. Espera a que termine el backup

### Paso 5: Ejecutar la Migración

**Opción A: Ejecutar Todo el Script**
1. Selecciona todo el contenido del script (Ctrl+A)
2. Click en el botón **"Execute SQL Script"** (▶️) o presiona **Ctrl+Enter**
3. Espera a que termine la ejecución

**Opción B: Ejecutar por Secciones**
1. Selecciona solo la sección que quieres ejecutar
2. Click en **"Execute SQL Statement"** (▶️) o presiona **Ctrl+Enter**
3. Repite para cada sección

### Paso 6: Verificar Resultados

Después de ejecutar, deberías ver mensajes como:
```
✅ Columna estado de pedidos_compra convertida a VARCHAR(20)
✅ CheckConstraint check_estado_pedido_valido creado correctamente
✅ Total de índices creados: 25
```

### Paso 7: Ejecutar Consultas de Verificación

Al final del script hay consultas comentadas. Descomenta y ejecuta:

```sql
-- Ver todos los índices creados
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'ix_%'
ORDER BY tablename, indexname;

-- Verificar constraint
SELECT conname, contype, pg_get_constraintdef(oid) as definition
FROM pg_constraint 
WHERE conname = 'check_estado_pedido_valido';

-- Verificar tipo de columna estado
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'pedidos_compra' 
AND column_name = 'estado';

-- Probar consulta optimizada
EXPLAIN ANALYZE 
SELECT * FROM pedidos_compra 
WHERE estado = 'borrador' 
ORDER BY fecha_pedido DESC 
LIMIT 10;
```

---

## ⚠️ Solución de Problemas

### Error: "relation does not exist"
- **Causa:** La tabla no existe en la base de datos
- **Solución:** Verifica que todas las tablas mencionadas existan. El script usa `IF EXISTS` para evitar errores, pero algunas tablas pueden no existir.

### Error: "permission denied"
- **Causa:** No tienes permisos para crear índices o modificar tablas
- **Solución:** Verifica que el usuario de la base de datos tenga permisos de `CREATE INDEX` y `ALTER TABLE`.

### Error: "index already exists"
- **Causa:** El índice ya existe (probablemente de una ejecución anterior)
- **Solución:** El script usa `CREATE INDEX IF NOT EXISTS`, así que esto no debería pasar. Si ocurre, puedes eliminar el índice manualmente o usar el script de rollback.

### Error: "constraint already exists"
- **Causa:** El constraint ya existe
- **Solución:** El script elimina el constraint antes de crearlo, así que esto no debería pasar. Si ocurre, elimínalo manualmente:
  ```sql
  ALTER TABLE pedidos_compra DROP CONSTRAINT IF EXISTS check_estado_pedido_valido;
  ```

---

## 🔄 Rollback (Revertir Cambios)

Si necesitas revertir la migración:

1. Abre el archivo **`rollback_migracion.sql`** en DBeaver
2. Ejecuta el script completo (Ctrl+Enter)
3. Esto eliminará todos los índices creados
4. **Nota:** El VARCHAR se mantiene (no se revierte a enum por simplicidad)

---

## 📊 Qué Hace la Migración

### 1. Cambia Enum a VARCHAR
- Convierte `pedidos_compra.estado` de enum PostgreSQL a `VARCHAR(20)`
- Normaliza valores existentes a minúsculas
- Agrega `CheckConstraint` para validación

### 2. Crea 25 Índices
- **Pedidos de compra:** 4 índices
- **Facturas:** 4 índices
- **Inventario:** 2 índices
- **Items:** 4 índices
- **Proveedores:** 2 índices
- **Recetas:** 2 índices
- **Programación:** 3 índices
- **Charolas:** 2 índices
- **Mermas:** 2 índices
- **Chat:** 4 índices

---

## ✅ Checklist Pre-Migración

- [ ] Backup de la base de datos realizado
- [ ] Conexión a DBeaver verificada
- [ ] Script SQL revisado
- [ ] Tablas existentes verificadas
- [ ] Permisos suficientes confirmados
- [ ] Ventana de mantenimiento programada (si es producción)

---

## ✅ Checklist Post-Migración

- [ ] Script ejecutado sin errores
- [ ] Mensajes de éxito verificados
- [ ] Índices creados verificados (25 índices)
- [ ] CheckConstraint creado verificando
- [ ] Consultas de prueba ejecutadas
- [ ] Rendimiento mejorado verificado

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los mensajes de error en DBeaver
2. Verifica los logs de PostgreSQL
3. Consulta `MIGRACION_INDICES_Y_ENUMS.md` para más detalles técnicos

---

**Última actualización:** 30 de Enero, 2026
