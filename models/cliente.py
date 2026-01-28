"""
Modelo de Cliente (CRM).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum

from models import db

class TipoCliente(enum.Enum):
    """Tipos de cliente."""
    PERSONA = 'persona'
    EMPRESA = 'empresa'

class Cliente(db.Model):
    """Modelo de cliente."""
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    tipo = Column(Enum(TipoCliente), nullable=False, default=TipoCliente.PERSONA)
    ruc_ci = Column(String(20), unique=True, nullable=True)  # RUC para empresas, CI para personas
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    notas = Column(Text, nullable=True)
    
    # Relaciones
    facturas = relationship('Factura', back_populates='cliente', lazy='dynamic')
    tickets = relationship('Ticket', back_populates='cliente', lazy='dynamic')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo.value if self.tipo else None,
            'ruc_ci': self.ruc_ci,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo,
            'notas': self.notas,
        }
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
