"""
Modelos de ProgramacionMenu y ProgramacionMenuItem.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from models import db

class TiempoComida(enum.Enum):
    """Tipos de tiempo de comida."""
    DESAYUNO = 'desayuno'
    ALMUERZO = 'almuerzo'
    CENA = 'cena'

class ProgramacionMenu(db.Model):
    """Modelo de programación de menú."""
    __tablename__ = 'programacion_menu'
    
    id = Column(Integer, primary_key=True)
    fecha_desde = Column(Date, nullable=False)  # Fecha de inicio del rango
    fecha_hasta = Column(Date, nullable=False)  # Fecha de fin del rango
    tiempo_comida = Column(Enum(TiempoComida), nullable=False)
    ubicacion = Column(String(100), nullable=False)  # restaurante_A, restaurante_B, etc.
    personas_estimadas = Column(Integer, nullable=False, default=0)
    charolas_planificadas = Column(Integer, nullable=False, default=0)  # Charolas planificadas para este servicio
    charolas_producidas = Column(Integer, nullable=False, default=0)  # Charolas producidas realmente
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    items = relationship('ProgramacionMenuItem', back_populates='programacion', cascade='all, delete-orphan')
    charolas = relationship('Charola', back_populates='programacion', lazy='dynamic')
    mermas_recetas = relationship('MermaRecetaProgramacion', back_populates='programacion', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        totales = self.calcular_totales_servicio()
        return {
            'id': self.id,
            'fecha_desde': self.fecha_desde.isoformat() if self.fecha_desde else None,
            'fecha_hasta': self.fecha_hasta.isoformat() if self.fecha_hasta else None,
            'fecha': self.fecha_desde.isoformat() if self.fecha_desde else None,  # Compatibilidad hacia atrás
            'tiempo_comida': self.tiempo_comida.value if self.tiempo_comida else None,
            'ubicacion': self.ubicacion,
            'personas_estimadas': self.personas_estimadas,
            'charolas_planificadas': self.charolas_planificadas,
            'charolas_producidas': self.charolas_producidas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'items': [item.to_dict() for item in self.items] if self.items else [],
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
        return f'<ProgramacionMenu {self.fecha_desde} a {self.fecha_hasta} - {self.tiempo_comida.value}>'

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
