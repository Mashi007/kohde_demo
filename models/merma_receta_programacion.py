"""
Modelo de Merma por Receta en Programación.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from models import db

class MermaRecetaProgramacion(db.Model):
    """Modelo de merma por receta en una programación específica."""
    __tablename__ = 'mermas_receta_programacion'
    
    id = Column(Integer, primary_key=True)
    programacion_id = Column(Integer, ForeignKey('programacion_menu.id'), nullable=False)
    receta_id = Column(Integer, ForeignKey('recetas.id'), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False, default=0)
    unidad = Column(String(20), nullable=False, default='g')
    costo_unitario = Column(Numeric(10, 2), nullable=False, default=0)
    costo_total = Column(Numeric(10, 2), nullable=False, default=0)
    motivo = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    registrado_por = Column(Integer, nullable=True)  # usuario_id
    
    # Constraint único: una merma por receta por programación
    __table_args__ = (
        UniqueConstraint('programacion_id', 'receta_id', name='uq_merma_receta_programacion'),
    )
    
    # Relaciones
    programacion = relationship('ProgramacionMenu', back_populates='mermas_recetas')
    receta = relationship('Receta', foreign_keys=[receta_id])
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'programacion_id': self.programacion_id,
            'receta_id': self.receta_id,
            'receta': self.receta.to_dict() if self.receta else None,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'unidad': self.unidad,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'costo_total': float(self.costo_total) if self.costo_total else 0,
            'motivo': self.motivo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'registrado_por': self.registrado_por,
            'programacion': {
                'id': self.programacion.id,
                'fecha': self.programacion.fecha.isoformat() if self.programacion.fecha else None,
                'tiempo_comida': self.programacion.tiempo_comida.value if self.programacion.tiempo_comida else None,
                'ubicacion': self.programacion.ubicacion,
            } if self.programacion else None,
        }
    
    def __repr__(self):
        return f'<MermaRecetaProgramacion {self.id} - Programacion {self.programacion_id} - Receta {self.receta_id}>'
