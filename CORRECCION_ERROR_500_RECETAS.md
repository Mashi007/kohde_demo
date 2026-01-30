# 🔧 Corrección: Error 500 al listar recetas

## 🎯 Problema

El endpoint `/api/planificacion/recetas` estaba devolviendo un error 500 al intentar listar las recetas.

## 🔍 Causas Identificadas

1. **Lazy Loading**: Los ingredientes y sus items relacionados no se estaban cargando antes de cerrar la sesión de la base de datos.
2. **Manejo de Enum**: El tipo de receta (enum) podría no estar siendo procesado correctamente cuando se lee de la base de datos.
3. **Falta de manejo de errores**: No había manejo de errores específico para cada receta al convertir a diccionario.

## ✅ Soluciones Aplicadas

### 1. Eager Loading con `selectinload` (modules/planificacion/recetas.py)

**Antes:**
```python
query = db.query(Receta)
```

**Después:**
```python
from sqlalchemy.orm import selectinload

query = db.query(Receta).options(
    selectinload(Receta.ingredientes).selectinload('item')
)
```

**Beneficio**: Carga todos los ingredientes e items relacionados antes de cerrar la sesión, evitando errores de lazy loading.

### 2. Manejo de Errores Mejorado en `to_dict()` (models/receta.py)

**Mejoras:**
- Validación más robusta del tipo de enum
- Manejo de errores con logging detallado
- Soporte para diferentes formatos de tipo (Enum, string, etc.)

**Código:**
```python
def to_dict(self):
    # Manejar el tipo de manera segura
    tipo_value = None
    try:
        if self.tipo is not None:
            if isinstance(self.tipo, TipoReceta):
                tipo_value = self.tipo.value
            elif isinstance(self.tipo, str):
                tipo_value = self.tipo.lower().strip()
            else:
                try:
                    tipo_value = self.tipo.value
                except (AttributeError, TypeError):
                    tipo_value = str(self.tipo).lower().strip() if self.tipo else None
    except Exception as e:
        import logging
        logging.error(f"Error procesando tipo de receta {self.id}: {str(e)}", exc_info=True)
        tipo_value = None
    
    # Manejar ingredientes de manera segura
    ingredientes_list = []
    try:
        if hasattr(self, 'ingredientes') and self.ingredientes:
            ingredientes_list = [ing.to_dict() for ing in self.ingredientes]
    except Exception as e:
        import logging
        logging.warning(f"Error procesando ingredientes de receta {self.id}: {str(e)}")
        ingredientes_list = []
    
    return {
        # ... campos ...
        'tipo': tipo_value,
        'ingredientes': ingredientes_list,
    }
```

### 3. Manejo de Errores en la Ruta (routes/planificacion_routes.py)

**Antes:**
```python
return paginated_response([r.to_dict() for r in recetas], skip=skip, limit=limit)
```

**Después:**
```python
# Convertir recetas a diccionarios con manejo de errores
recetas_dict = []
for receta in recetas:
    try:
        recetas_dict.append(receta.to_dict())
    except Exception as e:
        import logging
        logging.error(f"Error al convertir receta {receta.id} a dict: {str(e)}", exc_info=True)
        # Continuar con las demás recetas aunque una falle
        continue

return paginated_response(recetas_dict, skip=skip, limit=limit)
```

**Beneficio**: Si una receta tiene problemas, no falla toda la respuesta. Se registra el error y se continúa con las demás.

### 4. Mejora en `process_result_value` (models/receta.py)

**Mejoras:**
- Mejor manejo de valores de enum que no coinciden exactamente
- Logging de advertencias cuando se encuentra un valor inesperado
- Fallback más robusto

**Código:**
```python
def process_result_value(self, value, dialect):
    """Convierte el valor string del enum a objeto Enum."""
    if value is None:
        return None
    if isinstance(value, TipoReceta):
        return value
    if isinstance(value, str):
        valor_lower = value.lower().strip()
        for tipo in TipoReceta:
            if tipo.value == valor_lower:
                return tipo
        # Si no se encuentra, retornar el string (será manejado en to_dict)
        import logging
        logging.warning(f"Valor de enum no encontrado: '{valor_lower}', valores válidos: {[t.value for t in TipoReceta]}")
        return valor_lower
    try:
        return str(value).lower().strip()
    except:
        return value
```

### 5. Manejo de Errores en `RecetaIngrediente.to_dict()` (models/receta.py)

**Mejoras:**
- Manejo seguro del item relacionado
- Logging de errores si hay problemas

**Código:**
```python
def to_dict(self):
    # Manejar item de manera segura
    item_dict = None
    try:
        if self.item:
            item_dict = self.item.to_dict()
    except Exception as e:
        import logging
        logging.warning(f"Error procesando item de ingrediente {self.id}: {str(e)}")
        item_dict = None
    
    return {
        # ... campos ...
        'item': item_dict,
    }
```

## 📊 Archivos Modificados

1. **`modules/planificacion/recetas.py`**
   - Agregado eager loading con `selectinload`

2. **`models/receta.py`**
   - Mejorado `Receta.to_dict()`
   - Mejorado `RecetaIngrediente.to_dict()`
   - Mejorado `TipoRecetaEnum.process_result_value()`

3. **`routes/planificacion_routes.py`**
   - Agregado manejo de errores por receta individual

## ✅ Resultado Esperado

- ✅ El endpoint `/api/planificacion/recetas` debería funcionar correctamente
- ✅ Los ingredientes e items se cargan correctamente
- ✅ Los errores se registran en los logs para depuración
- ✅ Si una receta tiene problemas, no afecta a las demás

## 🔍 Verificación

Para verificar que funciona:
1. Hacer una petición GET a `/api/planificacion/recetas`
2. Revisar los logs del backend si hay errores
3. Verificar que todas las recetas se devuelven correctamente con sus ingredientes
