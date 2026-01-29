"""
Modelo de Charola (Bandeja/Plato servido).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship

from models import db

class Charola(db.Model):
    """Modelo de charola (bandeja/plato servido)."""
    __tablename__ = 'charolas'
    
    id = Column(Integer, primary_key=True)
    numero_charola = Column(String(50), unique=True, nullable=False)
    fecha_servicio = Column(DateTime, nullable=False, default=datetime.utcnow)
    ubicacion = Column(String(100), nullable=False)  # Restaurante/sucursal
    tiempo_comida = Column(String(50), nullable=False)  # desayuno, almuerzo, cena
    personas_servidas = Column(Integer, nullable=False, default=0)
    total_ventas = Column(Numeric(10, 2), nullable=False, default=0)
    costo_total = Column(Numeric(10, 2), nullable=False, default=0)
    ganancia = Column(Numeric(10, 2), nullable=False, default=0)
    observaciones = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    items_charola = relationship('CharolaItem', back_populates='charola', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'numero_charola': self.numero_charola,
            'fecha_servicio': self.fecha_servicio.isoformat() if self.fecha_servicio else None,
            'ubicacion': self.ubicacion,
            'tiempo_comida': self.tiempo_comida,
            'personas_servidas': self.personas_servidas,
            'total_ventas': float(self.total_ventas) if self.total_ventas else 0,
            'costo_total': float(self.costo_total) if self.costo_total else 0,
            'ganancia': float(self.ganancia) if self.ganancia else 0,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'items': [item.to_dict() for item in self.items_charola] if self.items_charola else []
        }
    
    def __repr__(self):
        return f'<Charola {self.numero_charola}>'

class CharolaItem(db.Model):
    """Items incluidos en una charola."""
    __tablename__ = 'charola_items'
    
    id = Column(Integer, primary_key=True)
    charola_id = Column(Integer, ForeignKey('charolas.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    receta_id = Column(Integer, ForeignKey('recetas.id'), nullable=True)
    nombre_item = Column(String(200), nullable=False)  # Nombre del item/receta
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    costo_subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    charola = relationship('Charola', back_populates='items_charola')
    item = relationship('Item', foreign_keys=[item_id])
    receta = relationship('Receta', foreign_keys=[receta_id])
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'charola_id': self.charola_id,
            'item_id': self.item_id,
            'receta_id': self.receta_id,
            'nombre_item': self.nombre_item,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else 0,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'subtotal': float(self.subtotal) if self.subtotal else 0,
            'costo_subtotal': float(self.costo_subtotal) if self.costo_subtotal else 0,
        }
    
    def __repr__(self):
        return f'<CharolaItem {self.nombre_item} - Charola {self.charola_id}>'
