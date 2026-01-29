"""
Modelo para almacenar costos estandarizados por item.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from models import db

class CostoItem(db.Model):
    """Modelo de costo estandarizado por item."""
    __tablename__ = 'costo_items'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    unidad_estandar = Column(String(20), nullable=False)  # Unidad estándar del item (viene del módulo Items) - Todas las facturas se convierten a esta unidad
    costo_unitario_promedio = Column(Numeric(10, 4), nullable=False)  # Costo promedio estandarizado
    variacion_porcentaje = Column(Numeric(10, 2), nullable=True)  # Variación porcentual entre facturas
    variacion_absoluta = Column(Numeric(10, 4), nullable=True)  # Variación absoluta (max - min)
    cantidad_facturas_usadas = Column(Integer, default=0, nullable=False)  # Número de facturas usadas para el cálculo
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    activo = Column(db.Boolean, default=True, nullable=False)
    notas = Column(Text, nullable=True)  # Notas sobre el cálculo o conversiones
    
    # Relaciones
    item = relationship('Item', back_populates='costo_estandarizado')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item': self.item.to_dict() if self.item else None,
            'unidad_estandar': self.unidad_estandar,
            'costo_unitario_promedio': float(self.costo_unitario_promedio) if self.costo_unitario_promedio else None,
            'variacion_porcentaje': float(self.variacion_porcentaje) if self.variacion_porcentaje else None,
            'variacion_absoluta': float(self.variacion_absoluta) if self.variacion_absoluta else None,
            'cantidad_facturas_usadas': self.cantidad_facturas_usadas,
            'fecha_calculo': self.fecha_calculo.isoformat() if self.fecha_calculo else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activo': self.activo,
            'notas': self.notas,
        }
    
    def __repr__(self):
        return f'<CostoItem {self.item_id} - {self.costo_unitario_promedio}/{self.unidad_estandar}>'
