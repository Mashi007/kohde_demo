"""
Modelos de Receta y RecetaIngrediente.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from models import db

class Receta(db.Model):
    """Modelo de receta."""
    __tablename__ = 'recetas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    porciones = Column(Integer, nullable=False, default=1)
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
    
    def calcular_totales(self):
        """Calcula calorías y costos totales basado en ingredientes."""
        from decimal import Decimal
        calorias_total = Decimal('0')
        costo_total = Decimal('0')
        
        for ingrediente in self.ingredientes:
            if ingrediente.item and ingrediente.item.calorias_por_unidad:
                # Calcular calorías: cantidad × calorías_por_unidad
                calorias_item = Decimal(str(ingrediente.cantidad)) * Decimal(str(ingrediente.item.calorias_por_unidad))
                calorias_total += calorias_item
            
            if ingrediente.item and ingrediente.item.costo_unitario_actual:
                # Calcular costo: cantidad × costo_unitario_actual
                costo_item = Decimal(str(ingrediente.cantidad)) * Decimal(str(ingrediente.item.costo_unitario_actual))
                costo_total += costo_item
        
        self.calorias_totales = calorias_total
        self.costo_total = costo_total
        
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
            'porciones': self.porciones,
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
