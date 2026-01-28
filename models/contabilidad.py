"""
Modelo de CuentaContable (Plan contable).
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models import db

class TipoCuenta(enum.Enum):
    """Tipos de cuenta contable."""
    ACTIVO = 'activo'
    PASIVO = 'pasivo'
    INGRESO = 'ingreso'
    GASTO = 'gasto'

class CuentaContable(db.Model):
    """Modelo de cuenta contable."""
    __tablename__ = 'cuentas_contables'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)  # ej: 1.1.01.001
    nombre = Column(String(200), nullable=False)
    tipo = Column(Enum(TipoCuenta), nullable=False)
    padre_id = Column(Integer, ForeignKey('cuentas_contables.id'), nullable=True)  # Para jerarquía
    descripcion = Column(Text, nullable=True)
    
    # Relaciones (auto-referencia para jerarquía)
    padre = relationship('CuentaContable', remote_side=[id], backref='hijos')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'tipo': self.tipo.value if self.tipo else None,
            'padre_id': self.padre_id,
            'descripcion': self.descripcion,
        }
    
    def __repr__(self):
        return f'<CuentaContable {self.codigo} - {self.nombre}>'
