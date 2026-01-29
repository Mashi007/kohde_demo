"""
Modelo de Item (Producto/Insumo).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models import db
from models.item_label import item_labels

class CategoriaItem(enum.Enum):
    """Categorías de items."""
    MATERIA_PRIMA = 'materia_prima'
    INSUMO = 'insumo'
    PRODUCTO_TERMINADO = 'producto_terminado'

class Item(db.Model):
    """Modelo de item (producto/insumo)."""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(Enum(CategoriaItem), nullable=False, default=CategoriaItem.INSUMO)
    unidad = Column(String(20), nullable=False)  # Unidad estándar del item (kg, litro, unidad, etc.) - Define la estandarización para todos los módulos
    calorias_por_unidad = Column(Numeric(10, 2), nullable=True)  # Calorías por unidad base
    proveedor_autorizado_id = Column(Integer, ForeignKey('proveedores.id'), nullable=True)
    tiempo_entrega_dias = Column(Integer, default=7, nullable=False)
    costo_unitario_actual = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    proveedor_autorizado = relationship('Proveedor', back_populates='items_autorizados')
    inventario = relationship('Inventario', back_populates='item', uselist=False)
    receta_ingredientes = relationship('RecetaIngrediente', back_populates='item', lazy='dynamic')
    requerimiento_items = relationship('RequerimientoItem', back_populates='item', lazy='dynamic')
    pedido_items = relationship('PedidoCompraItem', back_populates='item', lazy='dynamic')
    factura_items = relationship('FacturaItem', back_populates='item', lazy='dynamic')
    labels = relationship('ItemLabel', secondary=item_labels, back_populates='items', lazy='dynamic')
    costo_estandarizado = relationship('CostoItem', back_populates='item', uselist=False)
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria.value if self.categoria else None,
            'unidad': self.unidad,
            'calorias_por_unidad': float(self.calorias_por_unidad) if self.calorias_por_unidad else None,
            'proveedor_autorizado_id': self.proveedor_autorizado_id,
            'tiempo_entrega_dias': self.tiempo_entrega_dias,
            'costo_unitario_actual': float(self.costo_unitario_actual) if self.costo_unitario_actual else None,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'labels': [label.to_dict() for label in self.labels] if self.labels else [],
        }
    
    def __repr__(self):
        return f'<Item {self.codigo} - {self.nombre}>'
