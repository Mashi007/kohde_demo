"""
Modelo de Ticket (Sistema de servicio al cliente).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
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

class TipoTicketEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipoticket de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar validación automática."""
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('tipoticket', name='tipoticket', create_type=False))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, TipoTicket):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoTicket[valor_upper]
                return tipo_enum.name
            except KeyError:
                for tipo in TipoTicket:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoTicket")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, TipoTicket):
            return value
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                return TipoTicket[valor_upper]
            except KeyError:
                # Buscar por valor si no encuentra por nombre
                for tipo in TipoTicket:
                    if tipo.name.upper() == valor_upper or tipo.value.upper() == valor_upper:
                        return tipo
                return TipoTicket.CONSULTA
        return TipoTicket.CONSULTA

class EstadoTicketEnum(TypeDecorator):
    """TypeDecorator para manejar el enum estadoticket de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar validación automática."""
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('estadoticket', name='estadoticket', create_type=False))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, EstadoTicket):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip().replace(' ', '_')
            try:
                estado_enum = EstadoTicket[valor_upper]
                return estado_enum.name
            except KeyError:
                for estado in EstadoTicket:
                    if estado.value.lower() == value.lower().replace(' ', '_'):
                        return estado.name
                raise ValueError(f"'{value}' no es un valor válido para EstadoTicket")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, EstadoTicket):
            return value
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                return EstadoTicket[valor_upper]
            except KeyError:
                # Buscar por valor si no encuentra por nombre
                for estado in EstadoTicket:
                    if estado.name.upper() == valor_upper or estado.value.upper() == valor_upper:
                        return estado
                return EstadoTicket.ABIERTO
        return EstadoTicket.ABIERTO

class PrioridadTicketEnum(TypeDecorator):
    """TypeDecorator para manejar el enum prioridadticket de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar String para evitar validación automática."""
        return dialect.type_descriptor(SQLString(20))
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        from sqlalchemy import cast
        return cast(bindvalue, PG_ENUM('prioridadticket', name='prioridadticket', create_type=False))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, PrioridadTicket):
            return value.name
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                prioridad_enum = PrioridadTicket[valor_upper]
                return prioridad_enum.name
            except KeyError:
                for prioridad in PrioridadTicket:
                    if prioridad.value.lower() == value.lower():
                        return prioridad.name
                raise ValueError(f"'{value}' no es un valor válido para PrioridadTicket")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, PrioridadTicket):
            return value
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                return PrioridadTicket[valor_upper]
            except KeyError:
                # Buscar por valor si no encuentra por nombre
                for prioridad in PrioridadTicket:
                    if prioridad.name.upper() == valor_upper or prioridad.value.upper() == valor_upper:
                        return prioridad
                return PrioridadTicket.MEDIA
        return PrioridadTicket.MEDIA

class Ticket(db.Model):
    """Modelo de ticket."""
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, nullable=False, default=0)  # FK a clientes. Default 0 para tickets automáticos (cliente dummy)
    tipo = Column(TipoTicketEnum(), nullable=False)
    asunto = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(EstadoTicketEnum(), default=EstadoTicket.ABIERTO, nullable=False)
    prioridad = Column(PrioridadTicketEnum(), default=PrioridadTicket.MEDIA, nullable=False)
    asignado_a = Column(Integer, nullable=True)  # usuario_id
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_resolucion = Column(DateTime, nullable=True)
    respuesta = Column(Text, nullable=True)
    
    # Relaciones con otros módulos
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), nullable=True)
    pedido_id = Column(Integer, ForeignKey('pedidos_compra.id'), nullable=True)
    programacion_id = Column(Integer, ForeignKey('programacion_menu.id'), nullable=True)
    charola_id = Column(Integer, ForeignKey('charolas.id'), nullable=True)
    merma_id = Column(Integer, ForeignKey('mermas.id'), nullable=True)
    inventario_id = Column(Integer, ForeignKey('inventario.id'), nullable=True)
    
    # Relaciones SQLAlchemy
    proveedor = relationship('Proveedor', foreign_keys=[proveedor_id], lazy='joined')
    
    # Campos adicionales para contexto
    origen_modulo = Column(String(50), nullable=True)  # 'proveedor', 'programacion', 'charola', 'merma', 'inventario'
    auto_generado = Column(String(10), default='false', nullable=False)  # 'true' o 'false'
    
    # Relaciones removidas (módulo Cliente eliminado)
    
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
            'proveedor_id': self.proveedor_id,
            'proveedor': {
                'id': self.proveedor.id,
                'nombre': self.proveedor.nombre
            } if self.proveedor else None,
            'pedido_id': self.pedido_id,
            'programacion_id': self.programacion_id,
            'charola_id': self.charola_id,
            'merma_id': self.merma_id,
            'inventario_id': self.inventario_id,
            'origen_modulo': self.origen_modulo,
            'auto_generado': self.auto_generado == 'true',
        }
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.asunto}>'
