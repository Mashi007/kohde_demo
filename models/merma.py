"""
Modelo de Merma (Pérdidas/Desperdicios).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class TipoMerma(enum.Enum):
    """Tipos de merma."""
    VENCIMIENTO = 'vencimiento'
    DETERIORO = 'deterioro'
    PREPARACION = 'preparacion'
    SERVICIO = 'servicio'
    OTRO = 'otro'

class TipoMermaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipomerma de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(
                PG_ENUM('tipomerma', name='tipomerma', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('tipomerma', name='tipomerma', create_type=False))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoMerma):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoMerma[valor_upper]
                return tipo_enum.name
            except KeyError:
                for tipo in TipoMerma:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoMerma")
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoMerma):
            return value
        if isinstance(value, str):
            try:
                return TipoMerma[value.upper().strip()]
            except KeyError:
                return TipoMerma.OTRO
        return TipoMerma.OTRO

class Merma(db.Model):
    """Modelo de merma (pérdida/desperdicio)."""
    __tablename__ = 'mermas'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    fecha_merma = Column(DateTime, nullable=False, default=datetime.utcnow)
    tipo = Column(TipoMermaEnum(), nullable=False, default=TipoMerma.OTRO)
    cantidad = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(20), nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    costo_total = Column(Numeric(10, 2), nullable=False)
    motivo = Column(Text, nullable=True)
    ubicacion = Column(String(100), nullable=True)  # Restaurante/sucursal
    registrado_por = Column(Integer, nullable=True)  # usuario_id
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    item = relationship('Item', foreign_keys=[item_id])
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item': self.item.to_dict() if self.item else None,
            'fecha_merma': self.fecha_merma.isoformat() if self.fecha_merma else None,
            'tipo': self.tipo.value if self.tipo else None,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'unidad': self.unidad,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'costo_total': float(self.costo_total) if self.costo_total else 0,
            'motivo': self.motivo,
            'ubicacion': self.ubicacion,
            'registrado_por': self.registrado_por,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
    
    def __repr__(self):
        return f'<Merma {self.id} - Item {self.item_id}>'
