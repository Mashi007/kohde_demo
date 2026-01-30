"""
Modelo de CuentaContable (Plan contable).
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class TipoCuenta(enum.Enum):
    """Tipos de cuenta contable."""
    ACTIVO = 'activo'
    PASIVO = 'pasivo'
    INGRESO = 'ingreso'
    GASTO = 'gasto'

class TipoCuentaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipocuenta de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(
                PG_ENUM('tipocuenta', name='tipocuenta', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoCuenta):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoCuenta[valor_upper]
                return tipo_enum.name
            except KeyError:
                for tipo in TipoCuenta:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoCuenta")
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoCuenta):
            return value
        if isinstance(value, str):
            try:
                return TipoCuenta[value.upper().strip()]
            except KeyError:
                return TipoCuenta.ACTIVO
        return TipoCuenta.ACTIVO

class CuentaContable(db.Model):
    """Modelo de cuenta contable."""
    __tablename__ = 'cuentas_contables'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)  # ej: 1.1.01.001
    nombre = Column(String(200), nullable=False)
    tipo = Column(TipoCuentaEnum(), nullable=False)
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
