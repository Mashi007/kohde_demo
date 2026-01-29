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
        super().__init__(TipoReceta, native_enum=True, name='tiporeceta', create_constraint=True)
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su valor string antes de insertar."""
        if value is None:
            return None
        # Si es un objeto Enum, retornar su valor
        if isinstance(value, TipoReceta):
            return value.value
        # Si es un string, retornarlo directamente (ya debería ser el valor correcto)
        if isinstance(value, str):
            return value.lower()
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el valor string del enum a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, str):
            for tipo in TipoReceta:
                if tipo.value == value.lower():
                    return tipo
        return value

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
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo': self.tipo.value if self.tipo else None,
            'porciones': self.porciones,
            'porcion_gramos': float(self.porcion_gramos) if self.porcion_gramos else None,
            'calorias_totales': float(self.calorias_totales) if self.calorias_totales else None,
            'costo_total': float(self.costo_total) if self.costo_total else None,
            'calorias_por_porcion': float(self.calorias_por_porcion) if self.calorias_por_porcion else None,
            'costo_por_porcion': float(self.costo_por_porcion) if self.costo_por_porcion else None,
            'tiempo_preparacion': self.tiempo_preparacion,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ingredientes': [ing.to_dict() for ing in self.ingredientes] if self.ingredientes else [],
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
        return {
            'id': self.id,
            'receta_id': self.receta_id,
            'item_id': self.item_id,
            'cantidad': float(self.cantidad) if self.cantidad else None,
            'unidad': self.unidad,
            'item': self.item.to_dict() if self.item else None,
        }
    
    def __repr__(self):
        return f'<RecetaIngrediente {self.id} - Receta {self.receta_id}>'
