"""
Modelos de Receta y RecetaIngrediente.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum, TypeDecorator
from sqlalchemy.orm import relationship
import enum

from models import db

class TipoReceta(enum.Enum):
    """Tipos de receta según momento del día."""
    DESAYUNO = 'desayuno'
    ALMUERZO = 'almuerzo'
    CENA = 'cena'

class TipoRecetaEnum(TypeDecorator):
    """TypeDecorator para asegurar que SQLAlchemy use el valor del enum, no el nombre."""
    impl = Enum
    cache_ok = True
    
    def __init__(self):
        # Usar native_enum=False para que SQLAlchemy use los valores del enum directamente
        # PostgreSQL espera valores en MAYÚSCULAS (DESAYUNO, ALMUERZO, CENA)
        # pero nuestro enum Python usa minúsculas ('desayuno', 'almuerzo', 'cena')
        # La conversión se hace en process_bind_param y process_result_value
        super().__init__(
            TipoReceta, 
            native_enum=False,  # False = usar valores del enum, no nombres
            name='tiporeceta', 
            create_constraint=True
        )
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su nombre (MAYÚSCULAS) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        # Si es un objeto Enum, retornar su NOMBRE en mayúsculas (no el valor)
        # PostgreSQL espera: DESAYUNO, ALMUERZO, CENA (nombres del enum)
        if isinstance(value, TipoReceta):
            return value.name  # Usar el nombre del enum (DESAYUNO, ALMUERZO, CENA)
        # Si es un string, convertir a objeto Enum y luego obtener su nombre
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            # Buscar el enum por su valor (minúsculas)
            valores_validos = [e.value for e in TipoReceta]
            if valor_lower in valores_validos:
                # Encontrar el enum correspondiente y retornar su nombre
                for tipo in TipoReceta:
                    if tipo.value == valor_lower:
                        return tipo.name  # Retornar nombre del enum (DESAYUNO, ALMUERZO, CENA)
            # Si no está en valores, intentar buscar por nombre del enum (fallback)
            try:
                tipo_enum = TipoReceta[value.upper()]
                return tipo_enum.name  # Retornar nombre del enum
            except KeyError:
                raise ValueError(f"'{value}' no es un valor válido para TipoReceta. Valores válidos: {valores_validos}")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el nombre del enum (MAYÚSCULAS) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        # Si ya es un objeto Enum, retornarlo directamente
        if isinstance(value, TipoReceta):
            return value
        # Si es un string, PostgreSQL puede devolver:
        # 1. El nombre del enum en mayúsculas (DESAYUNO, ALMUERZO, CENA) - si usa native_enum
        # 2. El valor del enum en minúsculas ('desayuno', 'almuerzo', 'cena') - si usa valores
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            valor_lower = value.lower().strip()
            
            # Primero intentar buscar por nombre del enum (mayúsculas)
            try:
                return TipoReceta[valor_upper]  # Buscar por nombre del enum (DESAYUNO, ALMUERZO, CENA)
            except KeyError:
                pass
            
            # Si no se encuentra por nombre, buscar por valor (minúsculas)
            for tipo in TipoReceta:
                if tipo.value == valor_lower:
                    return tipo
            
            # Si no se encuentra, intentar buscar por nombre alternativo
            # Mapeo de valores comunes a nombres de enum
            valor_to_name = {
                'desayuno': 'DESAYUNO',
                'almuerzo': 'ALMUERZO',
                'cena': 'CENA',
            }
            if valor_lower in valor_to_name:
                try:
                    return TipoReceta[valor_to_name[valor_lower]]
                except KeyError:
                    pass
            
            # Si no se encuentra, retornar un valor por defecto seguro
            import logging
            logging.warning(f"Valor de enum no encontrado: '{value}' (upper: '{valor_upper}', lower: '{valor_lower}'), valores válidos: {[t.value for t in TipoReceta]}, nombres: {[t.name for t in TipoReceta]}, usando ALMUERZO como valor por defecto")
            return TipoReceta.ALMUERZO  # Valor por defecto seguro
        # Para cualquier otro tipo, intentar convertirlo a string
        try:
            str_value = str(value).upper().strip()
            try:
                return TipoReceta[str_value]
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
    tipo = Column(TipoRecetaEnum(), nullable=False, default=TipoReceta.ALMUERZO)
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
                            ingredientes_iterable = list(ingredientes) if not isinstance(ingredientes, list) else ingredientes
                            ingredientes_list = [ing.to_dict() for ing in ingredientes_iterable if ing is not None]
                        except Exception as e:
                            import logging
                            logging.warning(f"Error iterando ingredientes de receta {self.id}: {str(e)}")
                            ingredientes_list = []
        except Exception as e:
            import logging
            logging.warning(f"Error procesando ingredientes de receta {self.id}: {str(e)}", exc_info=True)
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
            if self.item:
                item_dict = self.item.to_dict()
        except Exception as e:
            import logging
            logging.warning(f"Error procesando item de ingrediente {self.id}: {str(e)}")
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
