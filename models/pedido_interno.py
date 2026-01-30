"""
Modelos de PedidoInterno y PedidoInternoItem.
Pedidos internos: transferencia de bodega a cocina.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class EstadoPedidoInterno(enum.Enum):
    """Estados de pedido interno."""
    PENDIENTE = 'pendiente'  # Creado pero no entregado
    ENTREGADO = 'entregado'  # Entregado a cocina
    CANCELADO = 'cancelado'  # Cancelado antes de entregar

class EstadoPedidoInternoEnum(TypeDecorator):
    """TypeDecorator para manejar el enum estadopedidointerno de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # PostgreSQL tiene valores en minúsculas: 'pendiente', 'entregado', 'cancelado'
            return dialect.type_descriptor(
                PG_ENUM('estadopedidointerno', values=['pendiente', 'entregado', 'cancelado'],
                       name='estadopedidointerno', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, EstadoPedidoInterno):
            return value.value.lower()  # 'pendiente', 'entregado', 'cancelado'
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            try:
                estado_enum = EstadoPedidoInterno[valor_lower.upper()]
                return estado_enum.value.lower()
            except KeyError:
                for estado in EstadoPedidoInterno:
                    if estado.value.lower() == valor_lower:
                        return estado.value.lower()
                raise ValueError(f"'{value}' no es un valor válido para EstadoPedidoInterno")
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, EstadoPedidoInterno):
            return value
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            for estado in EstadoPedidoInterno:
                if estado.value.lower() == valor_lower:
                    return estado
            return EstadoPedidoInterno.PENDIENTE
        return EstadoPedidoInterno.PENDIENTE

class PedidoInterno(db.Model):
    """Modelo de pedido interno (bodega → cocina)."""
    __tablename__ = 'pedidos_internos'
    
    id = Column(Integer, primary_key=True)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega = Column(DateTime, nullable=True)  # Fecha en que se entregó realmente
    estado = Column(EstadoPedidoInternoEnum(), default=EstadoPedidoInterno.PENDIENTE, nullable=False)
    
    # Quien entrega (responsable de bodega)
    entregado_por_id = Column(Integer, nullable=False)  # usuario_id del responsable de bodega
    entregado_por_nombre = Column(String(200), nullable=True)  # Nombre del responsable de bodega
    
    # Quien recibe (responsable de cocina)
    recibido_por_id = Column(Integer, nullable=True)  # usuario_id del responsable de cocina
    recibido_por_nombre = Column(String(200), nullable=True)  # Nombre del responsable de cocina
    
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    items = relationship('PedidoInternoItem', back_populates='pedido', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'estado': self.estado.value if self.estado else None,
            'entregado_por_id': self.entregado_por_id,
            'entregado_por_nombre': self.entregado_por_nombre,
            'recibido_por_id': self.recibido_por_id,
            'recibido_por_nombre': self.recibido_por_nombre,
            'observaciones': self.observaciones,
            'items': [item.to_dict() for item in self.items] if self.items else [],
            'total_items': len(self.items) if self.items else 0,
        }
    
    def __repr__(self):
        return f'<PedidoInterno {self.id} - Estado {self.estado.value}>'

class PedidoInternoItem(db.Model):
    """Modelo de item dentro de un pedido interno."""
    __tablename__ = 'pedido_interno_items'
    
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos_internos.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(20), nullable=True)  # Unidad de medida (kg, g, l, etc.)
    
    # Relaciones
    pedido = relationship('PedidoInterno', back_populates='items')
    item = relationship('Item')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'item_id': self.item_id,
            'cantidad': float(self.cantidad) if self.cantidad else None,
            'unidad': self.unidad,
            'item': self.item.to_dict() if self.item else None,
        }
    
    def __repr__(self):
        return f'<PedidoInternoItem {self.id} - Pedido {self.pedido_id} - Item {self.item_id}>'
