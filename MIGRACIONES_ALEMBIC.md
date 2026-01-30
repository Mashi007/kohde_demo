# Guía de Migraciones con Alembic

Este documento explica cómo usar Alembic para gestionar migraciones de base de datos en lugar de `db.create_all()`.

## ¿Por qué usar Alembic?

- ✅ **Control de versiones:** Las migraciones están versionadas y pueden revisarse
- ✅ **Rollback:** Permite revertir cambios de esquema
- ✅ **Colaboración:** Múltiples desarrolladores pueden aplicar los mismos cambios
- ✅ **Producción:** Cambios controlados y auditables en producción
- ✅ **Historial:** Registro completo de cambios en el esquema

## Instalación

Alembic ya está incluido en `requirements.txt`. Si necesitas instalarlo:

```bash
pip install alembic
```

## Inicialización (Primera vez)

Si Alembic no está inicializado en el proyecto, ejecuta:

```bash
alembic init alembic
```

Esto creará:
- `alembic/` - Directorio con configuración y migraciones
- `alembic.ini` - Archivo de configuración

## Configuración

### 1. Editar `alembic/env.py`

Asegúrate de que apunte a tu configuración:

```python
from config import Config
from models import db
from models import *  # Importar todos los modelos

# Usar la URI de la configuración
config.set_main_option('sqlalchemy.url', Config.SQLALCHEMY_DATABASE_URI)

# Importar metadata de los modelos
target_metadata = db.metadata
```

### 2. Editar `alembic.ini`

Verifica que la configuración sea correcta:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

**Nota:** En producción, esto se sobrescribe por la configuración en `env.py`.

## Uso Básico

### Crear una migración automática

```bash
# Alembic detectará cambios en los modelos
alembic revision --autogenerate -m "Descripción del cambio"
```

### Crear una migración manual

```bash
# Para cambios más complejos o personalizados
alembic revision -m "Descripción del cambio"
```

Luego edita el archivo generado en `alembic/versions/` para agregar las operaciones.

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar hasta una versión específica
alembic upgrade <revision_id>

# Ver estado actual
alembic current
```

### Revertir migraciones

```bash
# Revertir una migración
alembic downgrade -1

# Revertir hasta una versión específica
alembic downgrade <revision_id>

# Revertir todas
alembic downgrade base
```

### Ver historial

```bash
# Ver todas las migraciones
alembic history

# Ver migraciones pendientes
alembic heads
```

## En Producción (Render)

### Opción 1: Migraciones automáticas en el inicio

Agregar al `startCommand` en Render:

```bash
alembic upgrade head && gunicorn app:app --bind 0.0.0.0:$PORT
```

### Opción 2: Migraciones manuales

Ejecutar migraciones manualmente antes del despliegue o mediante script:

```bash
# Conectar a la base de datos de Render
psql $DATABASE_URL

# O ejecutar desde el servidor
alembic upgrade head
```

### Opción 3: Script de migración

Crear un script `scripts/run_migrations.py`:

```python
from app import create_app
from alembic.config import Config
from alembic import command

app = create_app()
with app.app_context():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

## Migración desde `db.create_all()`

### Paso 1: Crear migración inicial

```bash
# Esto creará una migración con el estado actual de la BD
alembic revision --autogenerate -m "Migración inicial desde create_all"
```

### Paso 2: Revisar la migración

Revisa el archivo generado en `alembic/versions/` para asegurarte de que es correcto.

### Paso 3: Aplicar en desarrollo

```bash
alembic upgrade head
```

### Paso 4: Desactivar `db.create_all()` en producción

Ya está implementado en `app.py` - solo se ejecuta si `DEBUG=True` o `ENVIRONMENT != 'production'`.

### Paso 5: Aplicar en producción

Ejecutar migraciones en producción antes del despliegue o en el inicio del servidor.

## Buenas Prácticas

1. **Siempre revisar migraciones autogeneradas** antes de aplicarlas
2. **Probar migraciones en desarrollo** antes de producción
3. **Hacer backup** antes de aplicar migraciones en producción
4. **Usar nombres descriptivos** para las migraciones
5. **No modificar migraciones ya aplicadas** - crear nuevas en su lugar
6. **Documentar cambios complejos** en el mensaje de la migración

## Comandos Útiles

```bash
# Ver diferencias entre modelos y BD actual
alembic revision --autogenerate -m "test" --sql

# Generar SQL sin aplicar
alembic upgrade head --sql

# Ver SQL de una migración específica
alembic upgrade <revision> --sql
```

## Troubleshooting

### Error: "Target database is not up to date"

```bash
# Ver estado actual
alembic current

# Aplicar migraciones pendientes
alembic upgrade head
```

### Error: "Can't locate revision identified by"

```bash
# Ver historial completo
alembic history

# Marcar la revisión actual manualmente (solo si es necesario)
alembic stamp head
```

### Conflictos de migraciones

Si hay conflictos entre ramas:

```bash
# Ver todas las cabezas
alembic heads

# Fusionar migraciones
alembic merge -m "Merge migraciones" <revision1> <revision2>
```

## Variables de Entorno

Asegúrate de que `DATABASE_URL` esté configurada correctamente en producción (Render la proporciona automáticamente).

## Notas Importantes

- ⚠️ **Nunca modificar migraciones ya aplicadas en producción**
- ⚠️ **Siempre hacer backup antes de migraciones importantes**
- ⚠️ **Probar migraciones en entorno de staging primero**
- ✅ **Usar `--autogenerate` con precaución** - siempre revisar los cambios
