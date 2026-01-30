"""
Modelo de Contacto (CRM).
Contactos de proveedores o colaboradores con capacidad de conversación.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class TipoContacto(enum.Enum):
    """Tipo de contacto."""
    PROVEEDOR = 'proveedor'
    COLABORADOR = 'colaborador'

class TipoContactoEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipocontacto de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(
                PG_ENUM('tipocontacto', values=['PROVEEDOR', 'COLABORADOR'],
                       name='tipocontacto', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoContacto):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoContacto[valor_upper]
                return tipo_enum.name
            except KeyError:
                for tipo in TipoContacto:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoContacto")
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoContacto):
            return value
        if isinstance(value, str):
            try:
                return TipoContacto[value.upper().strip()]
            except KeyError:
                return TipoContacto.PROVEEDOR
        return TipoContacto.PROVEEDOR

class Contacto(db.Model):
    """Modelo de contacto."""
    __tablename__ = 'contactos'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    whatsapp = Column(String(20), nullable=True)  # Número de WhatsApp
    proyecto = Column(String(200), nullable=True)  # Proyecto asociado
    cargo = Column(String(100), nullable=True)  # Cargo/posición
    tipo = Column(TipoContactoEnum(), nullable=False, default=TipoContacto.PROVEEDOR)
    
    # Relación con proveedor (opcional, solo si es tipo PROVEEDOR)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id', ondelete='SET NULL'), nullable=True)
    
    # Información adicional
    telefono = Column(String(20), nullable=True)
    notas = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    proveedor = relationship('Proveedor', backref='contactos', lazy='joined')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'whatsapp': self.whatsapp,
            'telefono': self.telefono,
            'proyecto': self.proyecto,
            'cargo': self.cargo,
            'tipo': self.tipo.value if self.tipo else None,
            'proveedor_id': self.proveedor_id,
            'proveedor': self.proveedor.to_dict() if self.proveedor else None,
            'notas': self.notas,
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
    
    def __repr__(self):
        return f'<Contacto {self.nombre} ({self.tipo.value if self.tipo else "N/A"})>'
