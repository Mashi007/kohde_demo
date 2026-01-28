"""
Modelo de Proveedor.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Integer as SQLInteger
from sqlalchemy.orm import relationship

from models import db

class Proveedor(db.Model):
    """Modelo de proveedor."""
    __tablename__ = 'proveedores'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    ruc = Column(String(20), unique=True, nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(Text, nullable=True)
    contacto_principal = Column(String(200), nullable=True)
    dias_credito = Column(SQLInteger, default=0, nullable=False)  # Días de crédito
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    facturas = relationship('Factura', back_populates='proveedor', lazy='dynamic')
    pedidos = relationship('PedidoCompra', back_populates='proveedor', lazy='dynamic')
    items_autorizados = relationship('Item', back_populates='proveedor_autorizado', lazy='dynamic')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ruc': self.ruc,
            'telefono': self.telefono,
            'email': self.email,
            'direccion': self.direccion,
            'contacto_principal': self.contacto_principal,
            'dias_credito': self.dias_credito,
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
        }
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'
