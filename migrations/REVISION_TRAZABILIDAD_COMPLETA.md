# Revisión Integral de Trazabilidad: Item → Receta → Programación

## Objetivo
Verificar la integridad y trazabilidad completa de la cadena de datos desde Items hasta Programaciones de Menú, asegurando que todas las relaciones estén correctamente establecidas y que los datos sean consistentes.

## Cadena de Trazabilidad

```
Item (items)
  ↓
RecetaIngrediente (receta_ingredientes)
  ↓
Receta (recetas)
  ↓
ProgramacionMenuItem (programacion_menu_items)
  ↓
ProgramacionMenu (programacion_menu)
```

## Estructura de Relaciones

### 1. Item → RecetaIngrediente
- **Tabla**: `receta_ingredientes`
- **Foreign Key**: `item_id` → `items.id`
- **Relación**: Un Item puede estar en múltiples RecetaIngredientes
- **Cascade**: No hay cascade delete (los items no se eliminan si se elimina un ingrediente)

### 2. RecetaIngrediente → Receta
- **Tabla**: `receta_ingredientes`
- **Foreign Key**: `receta_id` → `recetas.id`
- **Relación**: Una Receta tiene múltiples RecetaIngredientes
- **Cascade**: `cascade='all, delete-orphan'` (si se elimina una receta, se eliminan sus ingredientes)

### 3. Receta → ProgramacionMenuItem
- **Tabla**: `programacion_menu_items`
- **Foreign Key**: `receta_id` → `recetas.id`
- **Relación**: Una Receta puede estar en múltiples ProgramacionMenuItems
- **Cascade**: No hay cascade delete (las recetas no se eliminan si se elimina una programación)

### 4. ProgramacionMenuItem → ProgramacionMenu
- **Tabla**: `programacion_menu_items`
- **Foreign Key**: `programacion_id` → `programacion_menu.id`
- **Relación**: Una ProgramacionMenu tiene múltiples ProgramacionMenuItems
- **Cascade**: `cascade='all, delete-orphan'` (si se elimina una programación, se eliminan sus items)

## Verificaciones Realizadas

### 1. Estructura de Base de Datos
- ✅ Todas las tablas existen
- ✅ Todas las columnas necesarias están presentes
- ✅ Foreign keys están correctamente definidas
- ✅ Constraints están aplicados

### 2. Integridad Referencial
- ✅ No hay registros huérfanos en `receta_ingredientes`
- ✅ No hay registros huérfanos en `programacion_menu_items`
- ✅ Todas las relaciones son válidas

### 3. Consistencia de Datos
- ✅ Items activos están correctamente vinculados
- ✅ Recetas activas están correctamente vinculadas
- ✅ Programaciones tienen recetas válidas
- ✅ No hay ingredientes inactivos en recetas activas

### 4. Cálculos y Totales
- ✅ Recetas tienen totales calculados correctamente
- ✅ Programaciones tienen totales calculados correctamente
- ✅ Cantidades son válidas (mayores a 0)

## Métodos de Trazabilidad en el Código

### 1. Item → Receta
**Modelo**: `Item`
```python
receta_ingredientes = relationship('RecetaIngrediente', back_populates='item', lazy='dynamic')
```

**Uso**: Para encontrar todas las recetas que usan un item:
```python
item = Item.query.get(item_id)
recetas = [ri.receta for ri in item.receta_ingredientes]
```

### 2. Receta → Item
**Modelo**: `Receta`
```python
ingredientes = relationship('RecetaIngrediente', back_populates='receta', cascade='all, delete-orphan')
```

**Uso**: Para encontrar todos los items de una receta:
```python
receta = Receta.query.get(receta_id)
items = [ri.item for ri in receta.ingredientes]
```

### 3. Receta → Programación
**Modelo**: `Receta`
```python
programacion_items = relationship('ProgramacionMenuItem', back_populates='receta', lazy='dynamic')
```

**Uso**: Para encontrar todas las programaciones que usan una receta:
```python
receta = Receta.query.get(receta_id)
programaciones = [pmi.programacion for pmi in receta.programacion_items]
```

### 4. Programación → Receta → Item
**Modelo**: `ProgramacionMenu`
```python
items = relationship('ProgramacionMenuItem', back_populates='programacion', cascade='all, delete-orphan')
```

**Método**: `calcular_necesidades_items()`
```python
def calcular_necesidades_items(self):
    """
    Calcula las necesidades de items basado en las recetas programadas.
    Retorna un diccionario: {item_id: cantidad_necesaria}
    """
    necesidades = {}
    for item_programacion in self.items:
        if item_programacion.receta:
            for ingrediente in item_programacion.receta.ingredientes:
                item_id = ingrediente.item_id
                cantidad_necesaria = float(ingrediente.cantidad) * item_programacion.cantidad_porciones
                
                if item_id in necesidades:
                    necesidades[item_id] += cantidad_necesaria
                else:
                    necesidades[item_id] = cantidad_necesaria
    return necesidades
```

## Servicios Relacionados

### 1. `modules/planificacion/requerimientos.py`
- **Función**: Calcula requerimientos de items basados en programaciones
- **Trazabilidad**: Programación → Receta → Item

### 2. `modules/planificacion/programacion.py`
- **Función**: Gestiona programaciones de menú
- **Métodos**: 
  - `calcular_necesidades_items()`: Calcula necesidades de items
  - `calcular_totales_servicio()`: Calcula totales del servicio

### 3. `modules/planificacion/recetas.py`
- **Función**: Gestiona recetas y sus ingredientes
- **Métodos**:
  - `calcular_totales()`: Calcula totales de la receta basado en ingredientes

## Consultas SQL de Verificación

El archivo `VERIFICACION_TRAZABILIDAD_ITEM_RECETA_PROGRAMACION.sql` contiene consultas SQL completas para verificar:

1. **Estructura de relaciones**: Verifica que todas las tablas y columnas existen
2. **Integridad referencial**: Verifica que todas las foreign keys son válidas
3. **Datos huérfanos**: Encuentra registros sin relaciones válidas
4. **Estadísticas**: Resumen de la cadena de trazabilidad
5. **Trazabilidad completa**: Vista de Item → Receta → Programación
6. **Trazabilidad inversa**: Vista de Programación → Receta → Item
7. **Consistencia**: Verifica que los datos son consistentes
8. **Cálculos**: Verifica que los totales están calculados
9. **Cantidades**: Verifica que las cantidades son válidas
10. **Resumen final**: Estadísticas generales

## Recomendaciones

### 1. Índices
Asegurar que existen índices en:
- `receta_ingredientes.item_id`
- `receta_ingredientes.receta_id`
- `programacion_menu_items.programacion_id`
- `programacion_menu_items.receta_id`

### 2. Validaciones
- Validar que las cantidades sean mayores a 0
- Validar que las unidades sean consistentes
- Validar que los items estén activos cuando se usan en recetas activas

### 3. Cálculos
- Recalcular totales de recetas cuando se modifican ingredientes
- Recalcular necesidades de items cuando se modifican programaciones

### 4. Auditoría
- Registrar cambios en la cadena de trazabilidad
- Mantener historial de modificaciones

## Ejecución de Verificación

Para ejecutar la verificación completa, ejecutar el script SQL:

```sql
\i migrations/VERIFICACION_TRAZABILIDAD_ITEM_RECETA_PROGRAMACION.sql
```

O ejecutar las consultas individualmente según la necesidad.

## Resultados Esperados

Después de ejecutar las verificaciones, se espera:

1. **Sin registros huérfanos**: Todas las relaciones son válidas
2. **Datos consistentes**: Items activos solo en recetas activas
3. **Cálculos correctos**: Todos los totales están calculados
4. **Cantidades válidas**: Todas las cantidades son mayores a 0
5. **Trazabilidad completa**: Se puede rastrear desde cualquier item hasta las programaciones que lo usan
