"""
Modelos de PedidoCompra y PedidoCompraItem.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from models import db

# Valores válidos para estado de pedido (strings simples - más práctico)
ESTADOS_PEDIDO_VALIDOS = ['borrador', 'enviado', 'recibido', 'cancelado']
ESTADO_PEDIDO_DEFAULT = 'borrador'

# Clase simple para compatibilidad (reemplaza el enum complejo)
class EstadoPedido:
    """Estados de pedido como strings simples."""
    BORRADOR = 'borrador'
    ENVIADO = 'enviado'
    RECIBIDO = 'recibido'
    CANCELADO = 'cancelado'
    
    @classmethod
    def validar(cls, valor):
        """Valida que el valor sea un estado válido."""
        if isinstance(valor, str):
            valor_lower = valor.lower().strip()
            if valor_lower in ESTADOS_PEDIDO_VALIDOS:
                return valor_lower
        raise ValueError(f"Estado inválido: {valor}. Valores válidos: {ESTADOS_PEDIDO_VALIDOS}")

class PedidoCompra(db.Model):
    """Modelo de pedido de compra."""
    __tablename__ = 'pedidos_compra'
    
    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id', ondelete='RESTRICT'), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega_esperada = Column(DateTime, nullable=True)
    estado = Column(String(20), default=ESTADO_PEDIDO_DEFAULT, nullable=False)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    creado_por = Column(Integer, nullable=True)  # usuario_id
    observaciones = Column(Text, nullable=True)
    
    # Validación a nivel de base de datos
    __table_args__ = (
        CheckConstraint(
            "estado IN ('borrador', 'enviado', 'recibido', 'cancelado')",
            name='check_estado_pedido_valido'
        ),
    )
    
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
            'estado': self.estado if self.estado else None,
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
