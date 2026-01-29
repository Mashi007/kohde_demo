"""
Modelo de Inventario.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from models import db

class Inventario(db.Model):
    """Modelo de inventario."""
    __tablename__ = 'inventario'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id', ondelete='CASCADE'), unique=True, nullable=False)
    ubicacion = Column(String(100), nullable=False, default='bodega_principal')
    cantidad_actual = Column(Numeric(10, 2), nullable=False, default=0)
    cantidad_minima = Column(Numeric(10, 2), nullable=False, default=0)  # Amortiguador
    unidad = Column(String(20), nullable=False)
    ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    ultimo_costo_unitario = Column(Numeric(10, 2), nullable=True)
    
    # Relaciones
    item = relationship('Item', back_populates='inventario')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'ubicacion': self.ubicacion,
            'cantidad_actual': float(self.cantidad_actual) if self.cantidad_actual else None,
            'cantidad_minima': float(self.cantidad_minima) if self.cantidad_minima else None,
            'unidad': self.unidad,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None,
            'ultimo_costo_unitario': float(self.ultimo_costo_unitario) if self.ultimo_costo_unitario else None,
            'item': self.item.to_dict() if self.item else None,
        }
    
    def __repr__(self):
        return f'<Inventario Item {self.item_id} - Cantidad: {self.cantidad_actual}>'
