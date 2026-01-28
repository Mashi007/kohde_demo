"""
Modelo de Ticket (Sistema de servicio al cliente).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models import db

class TipoTicket(enum.Enum):
    """Tipos de ticket."""
    QUEJA = 'queja'
    CONSULTA = 'consulta'
    SUGERENCIA = 'sugerencia'
    RECLAMO = 'reclamo'

class EstadoTicket(enum.Enum):
    """Estados de ticket."""
    ABIERTO = 'abierto'
    EN_PROCESO = 'en_proceso'
    RESUELTO = 'resuelto'
    CERRADO = 'cerrado'

class PrioridadTicket(enum.Enum):
    """Prioridades de ticket."""
    BAJA = 'baja'
    MEDIA = 'media'
    ALTA = 'alta'
    URGENTE = 'urgente'

class Ticket(db.Model):
    """Modelo de ticket."""
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    tipo = Column(Enum(TipoTicket), nullable=False)
    asunto = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(Enum(EstadoTicket), default=EstadoTicket.ABIERTO, nullable=False)
    prioridad = Column(Enum(PrioridadTicket), default=PrioridadTicket.MEDIA, nullable=False)
    asignado_a = Column(Integer, nullable=True)  # usuario_id
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_resolucion = Column(DateTime, nullable=True)
    respuesta = Column(Text, nullable=True)
    
    # Relaciones
    cliente = relationship('Cliente', back_populates='tickets')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'tipo': self.tipo.value if self.tipo else None,
            'asunto': self.asunto,
            'descripcion': self.descripcion,
            'estado': self.estado.value if self.estado else None,
            'prioridad': self.prioridad.value if self.prioridad else None,
            'asignado_a': self.asignado_a,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_resolucion': self.fecha_resolucion.isoformat() if self.fecha_resolucion else None,
            'respuesta': self.respuesta,
        }
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.asunto}>'
