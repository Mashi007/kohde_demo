"""
Modelo para labels/clasificaciones internacionales de alimentos.
Basado en clasificaciones FAO/WHO y estándares internacionales para recetas.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models import db

# Tabla de relación muchos-a-muchos entre Items y Labels
item_labels = Table(
    'item_labels',
    db.Model.metadata,
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True),
    Column('label_id', Integer, ForeignKey('item_label.id'), primary_key=True)
)

class ItemLabel(db.Model):
    """Modelo de label/clasificación internacional para alimentos."""
    __tablename__ = 'item_label'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)  # Código internacional único
    nombre_es = Column(String(200), nullable=False)  # Nombre en español
    nombre_en = Column(String(200), nullable=False)  # Nombre en inglés
    descripcion = Column(Text, nullable=True)
    categoria_principal = Column(String(100), nullable=False)  # Categoría principal
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación muchos-a-muchos con Items
    items = relationship('Item', secondary=item_labels, back_populates='labels')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre_es': self.nombre_es,
            'nombre_en': self.nombre_en,
            'descripcion': self.descripcion,
            'categoria_principal': self.categoria_principal,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
    
    def __repr__(self):
        return f'<ItemLabel {self.codigo} - {self.nombre_es}>'
