"""
Modelos de Factura y FacturaItem.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.types import TypeDecorator, String as SQLString
import enum

from models import db

class TipoFactura(enum.Enum):
    """Tipos de factura."""
    CLIENTE = 'cliente'
    PROVEEDOR = 'proveedor'

class EstadoFactura(enum.Enum):
    """Estados de factura."""
    PENDIENTE = 'pendiente'
    PARCIAL = 'parcial'
    APROBADA = 'aprobada'
    RECHAZADA = 'rechazada'

class TipoFacturaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tipofactura de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar PG_ENUM para PostgreSQL."""
        if dialect.name == 'postgresql':
            # PostgreSQL tiene valores en MAYÚSCULAS: 'CLIENTE', 'PROVEEDOR'
            return dialect.type_descriptor(
                PG_ENUM('tipofactura', name='tipofactura', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su NOMBRE (mayúsculas) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        if isinstance(value, TipoFactura):
            return value.name  # 'CLIENTE' o 'PROVEEDOR'
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                tipo_enum = TipoFactura[valor_upper]
                return tipo_enum.name
            except KeyError:
                # Fallback: buscar por valor
                for tipo in TipoFactura:
                    if tipo.value.lower() == value.lower():
                        return tipo.name
                raise ValueError(f"'{value}' no es un valor válido para TipoFactura")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, TipoFactura):
            return value
        if isinstance(value, str):
            try:
                return TipoFactura[value.upper().strip()]
            except KeyError:
                return TipoFactura.CLIENTE  # Valor por defecto
        return TipoFactura.CLIENTE

class EstadoFacturaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum estadofactura de PostgreSQL."""
    impl = SQLString(20)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        """Cargar la implementación del dialecto - usar PG_ENUM para PostgreSQL."""
        if dialect.name == 'postgresql':
            # PostgreSQL tiene valores en MAYÚSCULAS: 'PENDIENTE', 'PARCIAL', 'APROBADA', 'RECHAZADA'
            return dialect.type_descriptor(
                PG_ENUM('estadofactura', name='estadofactura', create_type=False)
            )
        return dialect.type_descriptor(SQLString(20))
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su NOMBRE (mayúsculas) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        if isinstance(value, EstadoFactura):
            return value.name  # 'PENDIENTE', 'PARCIAL', etc.
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            try:
                estado_enum = EstadoFactura[valor_upper]
                return estado_enum.name
            except KeyError:
                # Fallback: buscar por valor
                for estado in EstadoFactura:
                    if estado.value.lower() == value.lower():
                        return estado.name
                raise ValueError(f"'{value}' no es un valor válido para EstadoFactura")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el NOMBRE (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        if isinstance(value, EstadoFactura):
            return value
        if isinstance(value, str):
            try:
                return EstadoFactura[value.upper().strip()]
            except KeyError:
                return EstadoFactura.PENDIENTE  # Valor por defecto
        return EstadoFactura.PENDIENTE

class Factura(db.Model):
    """Modelo de factura."""
    __tablename__ = 'facturas'
    
    id = Column(Integer, primary_key=True)
    numero_factura = Column(String(50), nullable=False)
    tipo = Column(TipoFacturaEnum(), nullable=False)
    # FK flexible: puede ser cliente_id o proveedor_id según el tipo
    # Nota: cliente_id mantenido para compatibilidad pero sin FK (tabla clientes removida)
    cliente_id = Column(Integer, nullable=True)  # Sin FK, tabla clientes no existe
    proveedor_id = Column(Integer, ForeignKey('proveedores.id', ondelete='SET NULL'), nullable=True)
    fecha_emision = Column(DateTime, nullable=False)
    fecha_recepcion = Column(DateTime, default=datetime.utcnow, nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    iva = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False)
    estado = Column(EstadoFacturaEnum(), default=EstadoFactura.PENDIENTE, nullable=False)
    imagen_url = Column(String(500), nullable=True)  # URL de la imagen de la factura
    items_json = Column(JSON, nullable=True)  # Datos extraídos por OCR
    aprobado_por = Column(Integer, nullable=True)  # usuario_id
    fecha_aprobacion = Column(DateTime, nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Información del remitente (quien envía por WhatsApp)
    remitente_nombre = Column(String(200), nullable=True)  # Nombre de quien envía
    remitente_telefono = Column(String(20), nullable=True)  # Teléfono de quien envía
    recibida_por_whatsapp = Column(Boolean, default=False, nullable=False)  # Si fue recibida por WhatsApp
    whatsapp_message_id = Column(String(100), nullable=True)  # ID del mensaje de WhatsApp
    
    # Relaciones
    # cliente removido (módulo Cliente eliminado)
    proveedor = relationship('Proveedor', back_populates='facturas')
    items = relationship('FacturaItem', back_populates='factura', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'numero_factura': self.numero_factura,
            'tipo': self.tipo.value if self.tipo else None,
            'cliente_id': self.cliente_id,
            'proveedor_id': self.proveedor_id,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'fecha_recepcion': self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'iva': float(self.iva) if self.iva else None,
            'total': float(self.total) if self.total else None,
            'estado': self.estado.value if self.estado else None,
            'imagen_url': self.imagen_url,
            'items_json': self.items_json,
            'aprobado_por': self.aprobado_por,
            'fecha_aprobacion': self.fecha_aprobacion.isoformat() if self.fecha_aprobacion else None,
            'observaciones': self.observaciones,
            'remitente_nombre': self.remitente_nombre,
            'remitente_telefono': self.remitente_telefono,
            'recibida_por_whatsapp': self.recibida_por_whatsapp,
            'whatsapp_message_id': self.whatsapp_message_id,
            'items': [item.to_dict() for item in self.items] if self.items else [],
        }
    
    def __repr__(self):
        return f'<Factura {self.numero_factura}>'

class FacturaItem(db.Model):
    """Modelo de item dentro de una factura."""
    __tablename__ = 'factura_items'
    
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey('facturas.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)  # Puede ser null si no se identifica el item
    cantidad_facturada = Column(Numeric(10, 2), nullable=False)
    cantidad_aprobada = Column(Numeric(10, 2), nullable=True)  # Se llena al aprobar
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(20), nullable=True)  # Unidad de la factura (qq, kg, l, etc.) - se usa para estandarización
    descripcion = Column(String(500), nullable=True)  # Descripción del item en la factura
    
    # Relaciones
    factura = relationship('Factura', back_populates='items')
    item = relationship('Item', back_populates='factura_items')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'factura_id': self.factura_id,
            'item_id': self.item_id,
            'cantidad_facturada': float(self.cantidad_facturada) if self.cantidad_facturada else None,
            'cantidad_aprobada': float(self.cantidad_aprobada) if self.cantidad_aprobada else None,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'unidad': self.unidad,
            'descripcion': self.descripcion,
        }
    
    def __repr__(self):
        return f'<FacturaItem {self.id} - Factura {self.factura_id}>'
