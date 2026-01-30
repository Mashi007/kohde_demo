"""
Modelos de ProgramacionMenu y ProgramacionMenuItem.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Enum, cast, literal
from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for
from sqlalchemy.types import TypeDecorator, String as SQLString
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
import enum

from models import db

class TiempoComida(enum.Enum):
    """Tipos de tiempo de comida."""
    DESAYUNO = 'desayuno'
    ALMUERZO = 'almuerzo'
    CENA = 'cena'

class TiempoComidaEnum(TypeDecorator):
    """TypeDecorator para manejar el enum tiempocomida de PostgreSQL.
    
    NOTA: Este TypeDecorator ya no se usa en el modelo ProgramacionMenu,
    que ahora usa PG_ENUM directamente. Se mantiene por compatibilidad.
    
    IMPORTANTE: PostgreSQL tiene valores en MAYÚSCULAS ('DESAYUNO', 'ALMUERZO', 'CENA'),
    pero Python usa valores en minúsculas ('desayuno', 'almuerzo', 'cena').
    Este decorator convierte entre ambos formatos.
    """
    impl = SQLString  # Usar String como base, no Enum, para evitar validación automática
    cache_ok = True
    
    def __init__(self):
        super().__init__(length=20)
    
    def bind_expression(self, bindvalue):
        """Agregar cast explícito al tipo enum de PostgreSQL."""
        # Cast explícito al tipo enum de PostgreSQL usando el tipo correcto
        return cast(bindvalue, PG_ENUM('tiempocomida', name='tiempocomida', create_type=False))
    
    def process_bind_param(self, value, dialect):
        """Convierte el enum a su NOMBRE (mayúsculas) antes de insertar en PostgreSQL."""
        if value is None:
            return None
        # PostgreSQL espera valores en MAYÚSCULAS: 'DESAYUNO', 'ALMUERZO', 'CENA'
        if isinstance(value, TiempoComida):
            # Usar el nombre del enum (mayúsculas)
            return value.name  # Usar el nombre del enum ('DESAYUNO', 'ALMUERZO', 'CENA')
        if isinstance(value, str):
            valor_lower = value.lower().strip()
            valor_upper = value.upper().strip()
            # Buscar el enum por su valor (minúsculas)
            valores_validos = [e.value for e in TiempoComida]
            if valor_lower in valores_validos:
                # Encontrar el enum por valor y retornar su nombre (mayúsculas)
                for tiempo in TiempoComida:
                    if tiempo.value == valor_lower:
                        return tiempo.name  # Retornar nombre en mayúsculas
            # Si no está en valores, intentar buscar por nombre del enum (mayúsculas)
            try:
                tiempo_enum = TiempoComida[valor_upper]
                return tiempo_enum.name  # Retornar nombre en mayúsculas
            except KeyError:
                raise ValueError(f"'{value}' no es un valor válido para TiempoComida. Valores válidos: {valores_validos}")
        return value
    
    def process_result_value(self, value, dialect):
        """Convierte el VALOR (mayúsculas) de PostgreSQL a objeto Enum."""
        if value is None:
            return None
        # Si ya es un objeto Enum, retornarlo directamente
        if isinstance(value, TiempoComida):
            return value
        # PostgreSQL devuelve valores en MAYÚSCULAS: 'DESAYUNO', 'ALMUERZO', 'CENA'
        if isinstance(value, str):
            valor_upper = value.upper().strip()
            valor_lower = value.lower().strip()
            
            # Primero intentar buscar por nombre del enum (mayúsculas) - caso normal
            try:
                return TiempoComida[valor_upper]  # Buscar por nombre (DESAYUNO, ALMUERZO, CENA)
            except KeyError:
                pass
            
            # Si no se encuentra por nombre, intentar buscar por valor (minúsculas) - fallback
            for tiempo in TiempoComida:
                if tiempo.value == valor_lower:
                    return tiempo
            
            # Si no se encuentra, retornar un valor por defecto seguro
            import logging
            logging.warning(f"Valor de enum no encontrado: '{value}' (upper: '{valor_upper}', lower: '{valor_lower}'), valores válidos: {[t.value for t in TiempoComida]}, nombres: {[t.name for t in TiempoComida]}, usando ALMUERZO como valor por defecto")
            return TiempoComida.ALMUERZO  # Valor por defecto seguro
        # Para cualquier otro tipo, intentar convertirlo a string
        try:
            str_value = str(value).upper().strip()
            try:
                return TiempoComida[str_value]
            except KeyError:
                return TiempoComida.ALMUERZO
        except:
            return TiempoComida.ALMUERZO

class ProgramacionMenu(db.Model):
    """Modelo de programación de menú."""
    __tablename__ = 'programacion_menu'
    
    id = Column(Integer, primary_key=True)
    # Compatibilidad: mantener fecha para bases de datos antiguas
    fecha = Column(Date, nullable=True)  # Mantener para compatibilidad hacia atrás
    # Columnas para rango de fechas (ya migradas en la BD)
    fecha_desde = Column(Date, nullable=False)  # Fecha de inicio del rango
    fecha_hasta = Column(Date, nullable=False)  # Fecha de fin del rango
    # PostgreSQL tiene valores en MAYÚSCULAS: 'DESAYUNO', 'ALMUERZO', 'CENA'
    # Usar values_callable para convertir nombres (mayúsculas) en lugar de valores (minúsculas)
    tiempo_comida = Column(PG_ENUM('tiempocomida', name='tiempocomida', create_type=False, values_callable=lambda x: [e.name for e in TiempoComida]), nullable=False)
    ubicacion = Column(String(100), nullable=False)  # restaurante_A, restaurante_B, etc.
    personas_estimadas = Column(Integer, nullable=False, default=0)
    charolas_planificadas = Column(Integer, nullable=False, default=0)  # Charolas planificadas para este servicio
    charolas_producidas = Column(Integer, nullable=False, default=0)  # Charolas producidas realmente
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @property
    def fecha_desde_effective(self):
        """Retorna fecha_desde si existe, sino fecha como fallback."""
        if self.fecha_desde is not None:
            return self.fecha_desde
        return self.fecha if self.fecha is not None else None
    
    @property
    def fecha_hasta_effective(self):
        """Retorna fecha_hasta si existe, sino fecha como fallback."""
        if self.fecha_hasta is not None:
            return self.fecha_hasta
        return self.fecha if self.fecha is not None else None
    
    # Relaciones
    items = relationship('ProgramacionMenuItem', back_populates='programacion', cascade='all, delete-orphan')
    charolas = relationship('Charola', back_populates='programacion', lazy='dynamic')
    mermas_recetas = relationship('MermaRecetaProgramacion', back_populates='programacion', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        try:
            totales = self.calcular_totales_servicio()
        except Exception as e:
            import logging
            logging.warning(f"Error al calcular totales para programación {self.id}: {str(e)}")
            totales = {
                'calorias_totales': 0,
                'costo_total': 0,
                'total_recetas': 0,
                'total_porciones': 0,
            }
        
        fecha_desde_eff = self.fecha_desde_effective
        fecha_hasta_eff = self.fecha_hasta_effective
        
        try:
            items_dict = [item.to_dict() for item in self.items] if self.items else []
        except Exception as e:
            import logging
            logging.warning(f"Error al convertir items de programación {self.id}: {str(e)}")
            items_dict = []
        
        return {
            'id': self.id,
            'fecha_desde': fecha_desde_eff.isoformat() if fecha_desde_eff else None,
            'fecha_hasta': fecha_hasta_eff.isoformat() if fecha_hasta_eff else None,
            'fecha': fecha_desde_eff.isoformat() if fecha_desde_eff else None,  # Compatibilidad hacia atrás
            'tiempo_comida': self.tiempo_comida.value if self.tiempo_comida else None,
            'ubicacion': self.ubicacion,
            'personas_estimadas': self.personas_estimadas,
            'charolas_planificadas': self.charolas_planificadas,
            'charolas_producidas': self.charolas_producidas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'items': items_dict,
            'calorias_totales': totales['calorias_totales'],
            'costo_total': totales['costo_total'],
            'total_recetas': totales['total_recetas'],
            'total_porciones': totales['total_porciones'],
        }
    
    def calcular_necesidades_items(self):
        """
        Calcula las necesidades de items basado en las recetas programadas.
        Retorna un diccionario: {item_id: cantidad_necesaria}
        """
        necesidades = {}
        for item_programacion in self.items:
            if item_programacion.receta:
                # Por cada ingrediente de la receta
                for ingrediente in item_programacion.receta.ingredientes:
                    item_id = ingrediente.item_id
                    # Cantidad necesaria = cantidad_por_porcion × cantidad_porciones
                    cantidad_necesaria = float(ingrediente.cantidad) * item_programacion.cantidad_porciones
                    
                    if item_id in necesidades:
                        necesidades[item_id] += cantidad_necesaria
                    else:
                        necesidades[item_id] = cantidad_necesaria
        return necesidades
    
    def calcular_totales_servicio(self):
        """
        Calcula calorías totales y costo total del servicio (menú).
        Retorna un diccionario con los totales calculados.
        """
        from decimal import Decimal
        
        calorias_totales = Decimal('0')
        costo_total = Decimal('0')
        total_recetas = len(self.items)
        total_porciones = 0
        
        for item_programacion in self.items:
            if item_programacion.receta:
                receta = item_programacion.receta
                cantidad_porciones = Decimal(str(item_programacion.cantidad_porciones))
                
                # Calorías: calorias_por_porcion × cantidad_porciones
                if receta.calorias_por_porcion:
                    calorias_receta = Decimal(str(receta.calorias_por_porcion)) * cantidad_porciones
                    calorias_totales += calorias_receta
                
                # Costo: costo_por_porcion × cantidad_porciones
                if receta.costo_por_porcion:
                    costo_receta = Decimal(str(receta.costo_por_porcion)) * cantidad_porciones
                    costo_total += costo_receta
                
                total_porciones += int(cantidad_porciones)
        
        return {
            'calorias_totales': float(calorias_totales),
            'costo_total': float(costo_total),
            'total_recetas': total_recetas,
            'total_porciones': total_porciones,
        }
    
    def __repr__(self):
        fecha_repr = self.fecha_desde_effective if self.fecha_desde_effective else (self.fecha if self.fecha else 'N/A')
        return f'<ProgramacionMenu {fecha_repr} - {self.tiempo_comida.value if self.tiempo_comida else "N/A"}>'

class ProgramacionMenuItem(db.Model):
    """Modelo de receta dentro de una programación de menú."""
    __tablename__ = 'programacion_menu_items'
    
    id = Column(Integer, primary_key=True)
    programacion_id = Column(Integer, ForeignKey('programacion_menu.id'), nullable=False)
    receta_id = Column(Integer, ForeignKey('recetas.id'), nullable=False)
    cantidad_porciones = Column(Integer, nullable=False, default=1)
    
    # Relaciones
    programacion = relationship('ProgramacionMenu', back_populates='items')
    receta = relationship('Receta', back_populates='programacion_items')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            'id': self.id,
            'programacion_id': self.programacion_id,
            'receta_id': self.receta_id,
            'cantidad_porciones': self.cantidad_porciones,
            'receta': self.receta.to_dict() if self.receta else None,
        }
    
    def __repr__(self):
        return f'<ProgramacionMenuItem {self.id} - Programacion {self.programacion_id}>'
