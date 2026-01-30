"""
Modelos de Requerimiento y RequerimientoItem.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Enum, Time
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class EstadoRequerimiento(enum.Enum):
    """Estados de requerimiento."""
    PENDIENTE = 'pendiente'
    ENTREGADO = 'entregado'
    CANCELADO = 'cancelado'

class EstadoRequerimientoEnum(TypeDecorator):
    """TypeDecorator para manejar el enum estadorequerimiento de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar validación automática."""
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('estadorequerimiento', name='estadorequerimiento', create_type=False))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, EstadoRequerimiento):
            return value.name  # 'PENDIENTE', 'ENTREGADO', 'CANCELADO'
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                estado_enum = EstadoRequerimiento[valor_upper]
                return estado_enum.name
            except KeyError:
                for estado in EstadoRequerimiento:
                    if estado.value.lower() == value.lower():
                        return estado.name
                raise ValueError(f"'{value}' no es un valor válido para EstadoRequerimiento")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, EstadoRequerimiento):
            return value
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                return EstadoRequerimiento[valor_upper]
            except KeyError:
                # Buscar por valor si no encuentra por nombre
                for estado in EstadoRequerimiento:
                    if estado.name.upper() == valor_upper or estado.value.upper() == valor_upper:
                        return estado
                return EstadoRequerimiento.PENDIENTE
        return EstadoRequerimiento.PENDIENTE

class Requerimiento(db.Model):
    """Modelo de requerimiento (salida de bodega)."""
    __tablename__ = 'requerimientos'
    
    id = Column(Integer, primary_key=True)
    solicitante = Column(Integer, nullable=False)  # usuario_id
    receptor = Column(Integer, nullable=False)  # usuario_id
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    estado = Column(EstadoRequerimientoEnum(), default=EstadoRequerimiento.PENDIENTE, nullable=False)
    observaciones = Column(String(500), nullable=True)
    
    # Relaciones
    items = relationship('RequerimientoItem', back_populates='requerimiento', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'solicitante': self.solicitante,
            'receptor': self.receptor,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado.value if self.estado else None,
            'observaciones': self.observaciones,
            'items': [item.to_dict() for item in self.items] if self.items else [],
        }
    
    def __repr__(self):
        return f'<Requerimiento {self.id}>'

class RequerimientoItem(db.Model):
    """Modelo de item dentro de un requerimiento."""
    __tablename__ = 'requerimiento_items'
    
    id = Column(Integer, primary_key=True)
    requerimiento_id = Column(Integer, ForeignKey('requerimientos.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    cantidad_solicitada = Column(Numeric(10, 2), nullable=False)
    cantidad_entregada = Column(Numeric(10, 2), nullable=True)
    hora_entrega = Column(Time, nullable=True)
    
    # Relaciones
    requerimiento = relationship('Requerimiento', back_populates='items')
    item = relationship('Item', back_populates='requerimiento_items')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'requerimiento_id': self.requerimiento_id,
            'item_id': self.item_id,
            'cantidad_solicitada': float(self.cantidad_solicitada) if self.cantidad_solicitada else None,
            'cantidad_entregada': float(self.cantidad_entregada) if self.cantidad_entregada else None,
            'hora_entrega': self.hora_entrega.isoformat() if self.hora_entrega else None,
            'item': self.item.to_dict() if self.item else None,
        }
    
    def __repr__(self):
        return f'<RequerimientoItem {self.id} - Requerimiento {self.requerimiento_id}>'
