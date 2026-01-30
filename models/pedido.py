"""
Modelos de PedidoCompra y PedidoCompraItem.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class EstadoPedido(enum.Enum):
    """Estados de pedido."""
    BORRADOR = 'borrador'
    ENVIADO = 'enviado'
    RECIBIDO = 'recibido'
    CANCELADO = 'cancelado'

class EstadoPedidoEnum(TypeDecorator):
    """TypeDecorator para manejar el enum estadopedido de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar validación automática."""
        # Usar String en lugar de PG_ENUM directamente para evitar problemas de validación
        # El cast se hace en bind_expression para escritura
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('estadopedido', name='estadopedido', create_type=False))
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su NOMBRE (mayúsculas) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        if isinstance(value, EstadoPedido):
            return value.name  # 'BORRADOR', 'ENVIADO', etc.
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                estado_enum = EstadoPedido[valor_upper]
                return estado_enum.name
            except KeyError:
                # Fallback: buscar por valor
                for estado in EstadoPedido:
                    if estado.value.lower() == value.lower():
                        return estado.name
                raise ValueError(f"'{value}' no es un valor válido para EstadoPedido")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, EstadoPedido):
            return value
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            # Intentar buscar por nombre del enum
            try:
                return EstadoPedido[valor_upper]
            except KeyError:
                # Si no encuentra por nombre, buscar por valor
                for estado in EstadoPedido:
                    if estado.name.upper() == valor_upper:
                        return estado
                    if estado.value.upper() == valor_upper:
                        return estado
                # Si aún no encuentra, retornar por defecto
                print(f"⚠️ Advertencia: Valor '{value}' no encontrado en EstadoPedido, usando BORRADOR por defecto")
                return EstadoPedido.BORRADOR
        return EstadoPedido.BORRADOR

class PedidoCompra(db.Model):
    """Modelo de pedido de compra."""
    __tablename__ = 'pedidos_compra'
    
    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id', ondelete='RESTRICT'), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega_esperada = Column(DateTime, nullable=True)
    estado = Column(EstadoPedidoEnum(), default=EstadoPedido.BORRADOR, nullable=False)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    creado_por = Column(Integer, nullable=True)  # usuario_id
    observaciones = Column(Text, nullable=True)
    
    # Relaciones
    proveedor = relationship('Proveedor', back_populates='pedidos')
    items = relationship('PedidoCompraItem', back_populates='pedido', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'proveedor_id': self.proveedor_id,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_entrega_esperada': self.fecha_entrega_esperada.isoformat() if self.fecha_entrega_esperada else None,
            'estado': self.estado.value if self.estado else None,
            'total': float(self.total) if self.total else None,
            'creado_por': self.creado_por,
            'observaciones': self.observaciones,
            'proveedor': self.proveedor.to_dict() if self.proveedor else None,
            'items': [item.to_dict() for item in self.items] if self.items else [],
        }
    
    def calcular_total(self):
        """Calcula el total del pedido sumando los items."""
        total = sum(float(item.subtotal) for item in self.items)
        self.total = total
        return total
    
    def __repr__(self):
        return f'<PedidoCompra {self.id} - Proveedor {self.proveedor_id}>'

class PedidoCompraItem(db.Model):
    """Modelo de item dentro de un pedido de compra."""
    __tablename__ = 'pedido_compra_items'
    
    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos_compra.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    pedido = relationship('PedidoCompra', back_populates='items')
    item = relationship('Item', back_populates='pedido_items')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'item_id': self.item_id,
            'cantidad': float(self.cantidad) if self.cantidad else None,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'item': self.item.to_dict() if self.item else None,
        }
    
    def __repr__(self):
        return f'<PedidoCompraItem {self.id} - Pedido {self.pedido_id}>'
