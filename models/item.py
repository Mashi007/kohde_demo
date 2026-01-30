"""
Modelo de Item (Producto/Insumo).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
import enum

from models import db
from models.item_label import item_labels

class CategoriaItem(enum.Enum):
    """Categorías de items."""
    MATERIA_PRIMA = 'materia_prima'
    INSUMO = 'insumo'
    PRODUCTO_TERMINADO = 'producto_terminado'
    BEBIDA = 'bebida'
    LIMPIEZA = 'limpieza'
    OTROS = 'otros'

class Item(db.Model):
    """Modelo de item (producto/insumo)."""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    # PostgreSQL tiene valores mixtos: algunos en MAYÚSCULAS (nombres) y otros en minúsculas (valores)
    # Mapeo: MATERIA_PRIMA, INSUMO, PRODUCTO_TERMINADO -> nombres (MAYÚSCULAS)
    #        BEBIDA, LIMPIEZA, OTROS -> valores (minúsculas)
    def _categoria_values():
        return ['MATERIA_PRIMA', 'INSUMO', 'PRODUCTO_TERMINADO', 'bebida', 'limpieza', 'otros']
    
    categoria = Column(
        PG_ENUM('categoriaitem', name='categoriaitem', create_type=False,
                values_callable=lambda x: _categoria_values()),
        nullable=False,
        default='INSUMO'  # Usar el valor que PostgreSQL espera
    )
    unidad = Column(String(20), nullable=False)  # Unidad estándar del item (kg, litro, unidad, etc.) - Define la estandarización para todos los módulos
    calorias_por_unidad = Column(Numeric(10, 2), nullable=True)  # Calorías por unidad base
    proveedor_autorizado_id = Column(Integer, ForeignKey('proveedores.id', ondelete='SET NULL'), nullable=True)
    tiempo_entrega_dias = Column(Integer, default=7, nullable=False)
    costo_unitario_actual = Column(Numeric(10, 2), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    proveedor_autorizado = relationship('Proveedor', back_populates='items_autorizados')
    inventario = relationship('Inventario', back_populates='item', uselist=False)
    receta_ingredientes = relationship('RecetaIngrediente', back_populates='item', lazy='dynamic')
    requerimiento_items = relationship('RequerimientoItem', back_populates='item', lazy='dynamic')
    pedido_items = relationship('PedidoCompraItem', back_populates='item', lazy='dynamic')
    factura_items = relationship('FacturaItem', back_populates='item', lazy='dynamic')
    labels = relationship('ItemLabel', secondary=item_labels, back_populates='items', lazy='select')
    costo_estandarizado = relationship('CostoItem', back_populates='item', uselist=False)
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        # Cargar labels de forma segura para evitar errores SQL
        labels_list = []
        try:
            # Con lazy='select', labels ya es una lista, no un query
            if self.labels:
                labels_list = [label.to_dict() for label in self.labels]
        except Exception as e:
            # Si hay un error cargando labels, simplemente retornar lista vacía
            import logging
            logging.warning(f"Error cargando labels para item {self.id}: {str(e)}")
            labels_list = []
        
        # Convertir categoria desde PostgreSQL (valores mixtos) a valor Python (minúsculas)
        categoria_value = None
        if self.categoria:
            if isinstance(self.categoria, CategoriaItem):
                categoria_value = self.categoria.value
            elif isinstance(self.categoria, str):
                # PostgreSQL puede devolver valores en mayúsculas (nombres) o minúsculas (valores)
                categoria_upper = self.categoria.upper()
                categoria_lower = self.categoria.lower()
                # Mapeo inverso: de valores PostgreSQL a valores Python
                pg_to_py_map = {
                    'MATERIA_PRIMA': 'materia_prima',
                    'INSUMO': 'insumo',
                    'PRODUCTO_TERMINADO': 'producto_terminado',
                    'BEBIDA': 'bebida',
                    'LIMPIEZA': 'limpieza',
                    'OTROS': 'otros',
                }
                categoria_value = pg_to_py_map.get(categoria_upper, categoria_lower)
            else:
                categoria_value = str(self.categoria).lower()
        
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': categoria_value,
            'unidad': self.unidad,
            'calorias_por_unidad': float(self.calorias_por_unidad) if self.calorias_por_unidad else None,
            'proveedor_autorizado_id': self.proveedor_autorizado_id,
            'tiempo_entrega_dias': self.tiempo_entrega_dias,
            'costo_unitario_actual': float(self.costo_unitario_actual) if self.costo_unitario_actual else None,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'labels': labels_list,
        }
    
    def __repr__(self):
        return f'<Item {self.codigo} - {self.nombre}>'
