"""
Modelos de Receta y RecetaIngrediente.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
import enum

from models import db

class TipoReceta(enum.Enum):
    """Tipos de receta según momento del día."""
    DESAYUNO = 'desayuno'
    ALMUERZO = 'almuerzo'
    CENA = 'cena'

class TipoRecetaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tiporeceta de PostgreSQL."""
    # Usar String como base para evitar validación automática incorrecta
    # PostgreSQL tiene valores en MINÚSCULAS: 'desayuno', 'almuerzo', 'cena'
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super().__init__(length=20)
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar problemas de validación."""
        # Usar String en lugar de PG_ENUM para evitar problemas de validación
        # El cast al tipo ENUM se hace en process_bind_param usando SQL explícito
        return dialect.type_descriptor(String(20))
    
    def coerce_compared_value(self, op, value):
        """Permitir comparaciones con strings directamente."""
        return self
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        # Hacer cast explícito al tipo ENUM de PostgreSQL solo para PostgreSQL
        # Esto genera SQL como: CAST(:tipo AS tiporeceta)
        return cast(bindvalue, PG_ENUM('tiporeceta', name='tiporeceta', create_type=False))
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su VALOR (minúsculas) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        # PostgreSQL espera valores en MINÚSCULAS: 'desayuno', 'almuerzo', 'cena'
        # Si es un objeto Enum, retornar su VALOR (minúsculas)
        if isinstance(value, TipoReceta):
            return value.value  # Usar el valor del enum ('desayuno', 'almuerzo', 'cena')
        # Si es un string, convertir a objeto Enum y luego obtener su valor
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            # Buscar el enum por su valor (minúsculas)
            valores_validos = [e.value for e in TipoReceta]
            if valor_lower in valores_validos:
                return valor_lower  # Retornar valor en minúsculas directamente
            # Si no está en valores, intentar buscar por nombre del enum (fallback)
            try:
                tipo_enum = TipoReceta[value.upper()]
                return tipo_enum.value  # Retornar valor del enum (minúsculas)
            except KeyError:
                raise ValueError(f"'{value}' no es un valor válido para TipoReceta. Valores válidos: {valores_validos}")
        return value
    
    
    def literal_processor(self, dialect):
        """Procesador literal para evitar el cast a VARCHAR."""
        def process(value):
            if isinstance(value, TipoReceta):
                return f"'{value.value}'::tiporeceta"
            if isinstance(value, str):
                valor_lower = value.lower().strip()
                valores_validos = [e.value for e in TipoReceta]
                if valor_lower in valores_validos:
                    return f"'{valor_lower}'::tiporeceta"
            return f"'{value}'::tiporeceta"
        return process
    
    def process_result_value(self, value, dialect):
        """Convierte el VALOR del enum (minúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        # Si ya es un objeto Enum, retornarlo directamente
        if isinstance(value, TipoReceta):
            return value
        # PostgreSQL devuelve valores en MINÚSCULAS: 'desayuno', 'almuerzo', 'cena'
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            valor_upper = value.upper().strip()
            
            # Primero intentar buscar por valor (minúsculas) - caso normal
            for tipo in TipoReceta:
                if tipo.value == valor_lower:
                    return tipo
            
            # Si no se encuentra por valor, intentar buscar por nombre del enum (mayúsculas) - fallback
            try:
                return TipoReceta[valor_upper]  # Buscar por nombre del enum (DESAYUNO, ALMUERZO, CENA)
            except KeyError:
                pass
            
            # Si no se encuentra, retornar un valor por defecto seguro
            import logging
            logging.warning(f"Valor de enum no encontrado: '{value}' (lower: '{valor_lower}', upper: '{valor_upper}'), valores válidos: {[t.value for t in TipoReceta]}, nombres: {[t.name for t in TipoReceta]}, usando ALMUERZO como valor por defecto")
            return TipoReceta.ALMUERZO  # Valor por defecto seguro
        # Para cualquier otro tipo, intentar convertirlo a string
        try:
            str_value = str(value).lower().strip()
            # Buscar por valor primero
            for tipo in TipoReceta:
                if tipo.value == str_value:
                    return tipo
            # Si no se encuentra, buscar por nombre
            try:
                return TipoReceta[str(value).upper().strip()]
            except KeyError:
                return TipoReceta.ALMUERZO  # Valor por defecto
        except:
            return TipoReceta.ALMUERZO  # Valor por defecto seguro

class Receta(db.Model):
    """Modelo de receta."""
    __tablename__ = 'recetas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    # Usar TypeDecorator para manejar correctamente los valores en minúsculas de PostgreSQL
    # El TypeDecorator convierte entre strings (DB) y enums (Python) automáticamente
    tipo = Column(
        TipoRecetaEnum(),
        nullable=False, 
        default='almuerzo'  # Usar el valor string directamente para el default
    )
    porciones = Column(Integer, nullable=False, default=1)
    porcion_gramos = Column(Numeric(10, 2), nullable=True)  # Peso total de la receta en gramos
    calorias_totales = Column(Numeric(10, 2), nullable=True)
    costo_total = Column(Numeric(10, 2), nullable=True)
    calorias_por_porcion = Column(Numeric(10, 2), nullable=True)
    costo_por_porcion = Column(Numeric(10, 2), nullable=True)
    tiempo_preparacion = Column(Integer, nullable=True)  # Minutos
    activa = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    ingredientes = relationship('RecetaIngrediente', back_populates='receta', cascade='all, delete-orphan')
    programacion_items = relationship('ProgramacionMenuItem', back_populates='receta', lazy='dynamic')
    mermas_programacion = relationship('MermaRecetaProgramacion', back_populates='receta', lazy='dynamic')
    
    def calcular_totales(self):
        """Calcula calorías, costos y peso total basado en ingredientes."""
        from decimal import Decimal
        from modules.logistica.conversor_unidades import convertir_a_gramos
        
        calorias_total = Decimal('0')
        costo_total = Decimal('0')
        peso_total_gramos = Decimal('0')
        
        for ingrediente in self.ingredientes:
            if not ingrediente.item:
                continue
                
            cantidad = Decimal(str(ingrediente.cantidad))
            unidad = ingrediente.unidad or ingrediente.item.unidad
            
            # Calcular calorías: cantidad × calorías_por_unidad
            if ingrediente.item.calorias_por_unidad:
                # Convertir cantidad a la unidad base del item para calcular calorías
                if unidad.lower() != ingrediente.item.unidad.lower():
                    # Si las unidades son diferentes, convertir primero
                    cantidad_base = convertir_a_gramos(cantidad, unidad) / convertir_a_gramos(Decimal('1'), ingrediente.item.unidad)
                    calorias_item = cantidad_base * Decimal(str(ingrediente.item.calorias_por_unidad))
                else:
                    calorias_item = cantidad * Decimal(str(ingrediente.item.calorias_por_unidad))
                calorias_total += calorias_item
            
            # Calcular costo: cantidad × costo_unitario_actual (convertido a unidad base)
            if ingrediente.item.costo_unitario_actual:
                # Convertir cantidad a la unidad base del item para calcular costo
                if unidad.lower() != ingrediente.item.unidad.lower():
                    cantidad_base = convertir_a_gramos(cantidad, unidad) / convertir_a_gramos(Decimal('1'), ingrediente.item.unidad)
                    costo_item = cantidad_base * Decimal(str(ingrediente.item.costo_unitario_actual))
                else:
                    costo_item = cantidad * Decimal(str(ingrediente.item.costo_unitario_actual))
                costo_total += costo_item
            
            # Calcular peso total en gramos
            try:
                peso_gramos = convertir_a_gramos(cantidad, unidad)
                peso_total_gramos += peso_gramos
            except:
                # Si no se puede convertir, intentar usar cantidad directamente si ya está en gramos
                if unidad.lower() in ['g', 'gramo', 'gramos']:
                    peso_total_gramos += cantidad
        
        self.calorias_totales = calorias_total
        self.costo_total = costo_total
        self.porcion_gramos = peso_total_gramos
        
        # Calcular por porción
        if self.porciones > 0:
            self.calorias_por_porcion = calorias_total / Decimal(str(self.porciones))
            self.costo_por_porcion = costo_total / Decimal(str(self.porciones))
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        # Manejar el tipo de manera segura
        tipo_value = None
        try:
            if self.tipo:
                if isinstance(self.tipo, TipoReceta):
                    # Si es un objeto Enum, obtener su valor
                    tipo_value = self.tipo.value
                elif isinstance(self.tipo, str):
                    # Si es un string, usarlo directamente (normalizar a minúsculas)
                    tipo_value = self.tipo.lower().strip()
                else:
                    # Intentar obtener el valor si tiene el atributo value
                    try:
                        tipo_value = self.tipo.value
                    except (AttributeError, TypeError):
                        tipo_value = str(self.tipo).lower().strip() if self.tipo else None
        except Exception as e:
            # Si hay algún error, usar 'almuerzo' como valor por defecto seguro
            import logging
            logging.warning(f"Error procesando tipo de receta {self.id if hasattr(self, 'id') else 'N/A'}: {str(e)}", exc_info=True)
            tipo_value = 'almuerzo'  # Valor por defecto seguro
        
        # Asegurar que tipo_value sea válido
        if tipo_value is None:
            tipo_value = 'almuerzo'  # Valor por defecto
        elif tipo_value not in ['desayuno', 'almuerzo', 'cena']:
            # Si el valor no es válido, usar 'almuerzo' como fallback
            import logging
            logging.warning(f"Valor de tipo inválido '{tipo_value}' para receta {self.id if hasattr(self, 'id') else 'N/A'}, usando 'almuerzo'")
            tipo_value = 'almuerzo'
        
        # Manejar ingredientes de manera segura
        ingredientes_list = []
        try:
            if hasattr(self, 'ingredientes'):
                # Verificar si ingredientes es una colección válida
                ingredientes = self.ingredientes
                if ingredientes is not None:
                    # Si es una relación lazy, podría ser un objeto Query o una lista
                    if hasattr(ingredientes, '__iter__'):
                        try:
                            # Intentar convertir a lista si es necesario
                            # Verificar si es un query object o una lista
                            if hasattr(ingredientes, 'all'):
                                # Es un query object, ejecutarlo
                                ingredientes_iterable = ingredientes.all()
                            elif isinstance(ingredientes, list):
                                ingredientes_iterable = ingredientes
                            else:
                                # Intentar convertir a lista
                                ingredientes_iterable = list(ingredientes)
                            
                            # Procesar cada ingrediente con manejo de errores individual
                            for ing in ingredientes_iterable:
                                if ing is not None:
                                    try:
                                        ing_dict = ing.to_dict()
                                        ingredientes_list.append(ing_dict)
                                    except Exception as ing_error:
                                        import logging
                                        logging.warning(f"Error serializando ingrediente {ing.id if hasattr(ing, 'id') else 'N/A'} de receta {self.id}: {str(ing_error)}")
                                        # Continuar con el siguiente ingrediente
                                        continue
                        except Exception as e:
                            import logging
                            import traceback
                            logging.warning(f"Error iterando ingredientes de receta {self.id}: {str(e)}")
                            logging.debug(traceback.format_exc())
                            ingredientes_list = []
        except Exception as e:
            import logging
            import traceback
            logging.warning(f"Error procesando ingredientes de receta {self.id}: {str(e)}", exc_info=True)
            logging.debug(traceback.format_exc())
            ingredientes_list = []
        
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo': tipo_value,
            'porciones': self.porciones,
            'porcion_gramos': float(self.porcion_gramos) if self.porcion_gramos else None,
            'calorias_totales': float(self.calorias_totales) if self.calorias_totales else None,
            'costo_total': float(self.costo_total) if self.costo_total else None,
            'calorias_por_porcion': float(self.calorias_por_porcion) if self.calorias_por_porcion else None,
            'costo_por_porcion': float(self.costo_por_porcion) if self.costo_por_porcion else None,
            'tiempo_preparacion': self.tiempo_preparacion,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ingredientes': ingredientes_list,
        }
    
    def __repr__(self):
        return f'<Receta {self.nombre}>'

class RecetaIngrediente(db.Model):
    """Modelo de ingrediente dentro de una receta."""
    __tablename__ = 'receta_ingredientes'
    
    id = Column(Integer, primary_key=True)
    receta_id = Column(Integer, ForeignKey('recetas.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(20), nullable=False)
    
    # Relaciones
    receta = relationship('Receta', back_populates='ingredientes')
    item = relationship('Item', back_populates='receta_ingredientes')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        # Manejar item de manera segura
        item_dict = None
        try:
            if hasattr(self, 'item') and self.item:
                try:
                    item_dict = self.item.to_dict()
                except Exception as item_error:
                    import logging
                    import traceback
                    logging.warning(f"Error serializando item {self.item_id} de ingrediente {self.id}: {str(item_error)}")
                    logging.debug(traceback.format_exc())
                    # Crear un dict básico del item si falla la serialización completa
                    try:
                        item_dict = {
                            'id': self.item.id if hasattr(self.item, 'id') else self.item_id,
                            'codigo': self.item.codigo if hasattr(self.item, 'codigo') else None,
                            'nombre': self.item.nombre if hasattr(self.item, 'nombre') else 'Item no disponible',
                            'unidad': self.item.unidad if hasattr(self.item, 'unidad') else None,
                        }
                    except:
                        item_dict = None
        except Exception as e:
            import logging
            import traceback
            logging.warning(f"Error procesando item de ingrediente {self.id}: {str(e)}")
            logging.debug(traceback.format_exc())
            item_dict = None
        
        return {
            'id': self.id,
            'receta_id': self.receta_id,
            'item_id': self.item_id,
            'cantidad': float(self.cantidad) if self.cantidad else None,
            'unidad': self.unidad,
            'item': item_dict,
        }
    
    def __repr__(self):
        return f'<RecetaIngrediente {self.id} - Receta {self.receta_id}>'
