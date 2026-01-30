"""
Modelo de Conversación con Contactos (CRM).
Historial de conversaciones por email y WhatsApp con contactos.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from models import db

class TipoMensajeContacto(enum.Enum):
    """Tipo de mensaje en conversación."""
    EMAIL = 'email'
    WHATSAPP = 'whatsapp'

class DireccionMensaje(enum.Enum):
    """Dirección del mensaje."""
    ENVIADO = 'enviado'  # Mensaje enviado por nosotros
    RECIBIDO = 'recibido'  # Mensaje recibido (futuro)

class ConversacionContacto(db.Model):
    """Modelo de conversación con un contacto."""
    __tablename__ = 'conversaciones_contactos'
    
    id = Column(Integer, primary_key=True)
    contacto_id = Column(Integer, ForeignKey('contactos.id', ondelete='CASCADE'), nullable=False)
    tipo_mensaje = Column(SQLEnum(TipoMensajeContacto), nullable=False)  # email o whatsapp
    direccion = Column(SQLEnum(DireccionMensaje), nullable=False, default=DireccionMensaje.ENVIADO)
    
    # Contenido del mensaje
    asunto = Column(String(500), nullable=True)  # Solo para emails
    contenido = Column(Text, nullable=False)
    
    # Metadatos
    mensaje_id_externo = Column(String(200), nullable=True)  # ID del mensaje en WhatsApp/Email service
    estado = Column(String(50), default='enviado')  # enviado, entregado, leido, error
    error = Column(Text, nullable=True)  # Mensaje de error si falló
    
    fecha_envio = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    # Relación con Contacto - usar lazy='select' para evitar problemas si la tabla no existe aún
    contacto = relationship('Contacto', backref='conversaciones', lazy='select')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'contacto_id': self.contacto_id,
            'contacto': self.contacto.to_dict() if self.contacto else None,
            'tipo_mensaje': self.tipo_mensaje.value if self.tipo_mensaje else None,
            'direccion': self.direccion.value if self.direccion else None,
            'asunto': self.asunto,
            'contenido': self.contenido,
            'mensaje_id_externo': self.mensaje_id_externo,
            'estado': self.estado,
            'error': self.error,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
    
    def __repr__(self):
        return f'<ConversacionContacto {self.id} - {self.tipo_mensaje.value if self.tipo_mensaje else "N/A"}>'
