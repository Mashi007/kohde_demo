"""
Modelo de Chat AI (Conversaciones y Mensajes).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class TipoMensaje(enum.Enum):
    """Tipos de mensaje."""
    USUARIO = 'usuario'
    ASISTENTE = 'asistente'
    SISTEMA = 'sistema'

class TipoMensajeEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipomensaje de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(
                PG_ENUM('tipomensaje', name='tipomensaje', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoMensaje):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoMensaje[valor_upper]
                return tipo_enum.name
            except KeyError:
                for tipo in TipoMensaje:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoMensaje")
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoMensaje):
            return value
        if isinstance(value, str):
            try:
                return TipoMensaje[value.upper().strip()]
            except KeyError:
                return TipoMensaje.USUARIO
        return TipoMensaje.USUARIO

class Conversacion(db.Model):
    """Modelo de conversación de chat."""
    __tablename__ = 'conversaciones'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=True)
    usuario_id = Column(Integer, nullable=True)  # ID del usuario (si hay autenticación)
    contexto_modulo = Column(String(50), nullable=True)  # crm, logistica, contabilidad, etc.
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    activa = Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    mensajes = relationship('Mensaje', back_populates='conversacion', cascade='all, delete-orphan', order_by='Mensaje.fecha_envio')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'usuario_id': self.usuario_id,
            'contexto_modulo': self.contexto_modulo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'activa': self.activa,
            'total_mensajes': len(self.mensajes) if self.mensajes else 0
        }
    
    def __repr__(self):
        return f'<Conversacion {self.id} - {self.titulo}>'

class Mensaje(db.Model):
    """Modelo de mensaje en una conversación."""
    __tablename__ = 'mensajes'
    
    id = Column(Integer, primary_key=True)
    conversacion_id = Column(Integer, ForeignKey('conversaciones.id'), nullable=False)
    tipo = Column(TipoMensajeEnum(), nullable=False, default=TipoMensaje.USUARIO)
    contenido = Column(Text, nullable=False)
    tokens_usados = Column(Integer, nullable=True)  # Tokens usados en la respuesta del AI
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    conversacion = relationship('Conversacion', back_populates='mensajes')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'conversacion_id': self.conversacion_id,
            'tipo': self.tipo.value if self.tipo else None,
            'contenido': self.contenido,
            'tokens_usados': self.tokens_usados,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
        }
    
    def __repr__(self):
        return f'<Mensaje {self.id} - {self.tipo.value}>'
