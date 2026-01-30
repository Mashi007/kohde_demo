"""
Servicio para calcular requerimientos de items basado en programación quincenal.
Calcula qué items se necesitan considerando recetas programadas e inventario actual.
"""
from typing import List, Dict
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import ProgramacionMenu, Receta, RecetaIngrediente, Inventario, Item, Proveedor

class RequerimientosService:
    """Servicio para cálculo de requerimientos de items."""
    
    @staticmethod
    def calcular_requerimientos_quincenales(
        db: Session,
        fecha_inicio: date,
        fecha_fin: date = None
    ) -> Dict:
        """
        Calcula los requerimientos de items para un período quincenal.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio del período (normalmente hoy)
            fecha_fin: Fecha de fin del período (15 días después si no se especifica)
            
        Returns:
            Diccionario con requerimientos calculados
        """
        if fecha_fin is None:
            fecha_fin = fecha_inicio + timedelta(days=15)
        
        # Obtener todas las programaciones que se solapan con el período
        programaciones = db.query(ProgramacionMenu).filter(
            and_(
                ProgramacionMenu.fecha_hasta >= fecha_inicio,
                ProgramacionMenu.fecha_desde <= fecha_fin
            )
        ).all()
        
        # Calcular necesidades totales de items
        necesidades_totales = {}  # {item_id: cantidad_necesaria}
        
        for programacion in programaciones:
            necesidades = programacion.calcular_necesidades_items()
            for item_id, cantidad in necesidades.items():
                if item_id in necesidades_totales:
                    necesidades_totales[item_id] += cantidad
                else:
                    necesidades_totales[item_id] = cantidad
        
        # Obtener inventario actual y calcular faltantes
        requerimientos = []
        
        for item_id, cantidad_necesaria in necesidades_totales.items():
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item or not item.activo:
                continue
            
            # Obtener inventario del item
            inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
            cantidad_actual = float(inventario.cantidad_actual) if inventario else 0
            cantidad_minima = float(inventario.cantidad_minima) if inventario else 0
            
            # Calcular cantidad a pedir:
            # cantidad_necesaria (de programación) + cantidad_minima - cantidad_actual
            cantidad_a_pedir = cantidad_necesaria + cantidad_minima - cantidad_actual
            
            # Solo agregar si realmente se necesita pedir
            if cantidad_a_pedir > 0:
                requerimientos.append({
                    'item_id': item_id,
                    'item': item,
                    'cantidad_necesaria': cantidad_necesaria,
                    'cantidad_actual': cantidad_actual,
                    'cantidad_minima': cantidad_minima,
                    'cantidad_a_pedir': cantidad_a_pedir,
                    'unidad': item.unidad,
                    'proveedor_id': item.proveedor_autorizado_id,
                    'proveedor': item.proveedor_autorizado if item.proveedor_autorizado else None
                })
        
        return {
            'fecha_inicio': fecha_inicio.isoformat(),
            'fecha_fin': fecha_fin.isoformat(),
            'total_programaciones': len(programaciones),
            'requerimientos': requerimientos,
            'total_items_necesarios': len(requerimientos)
        }
    
    @staticmethod
    def agrupar_requerimientos_por_proveedor(requerimientos: List[Dict]) -> Dict:
        """
        Agrupa requerimientos por proveedor.
        
        Args:
            requerimientos: Lista de requerimientos calculados
            
        Returns:
            Diccionario agrupado por proveedor_id
        """
        por_proveedor = {}
        
        for req in requerimientos:
            proveedor_id = req.get('proveedor_id')
            
            # Si no tiene proveedor autorizado, usar "sin_proveedor"
            if not proveedor_id:
                proveedor_id = 'sin_proveedor'
            
            if proveedor_id not in por_proveedor:
                por_proveedor[proveedor_id] = {
                    'proveedor_id': proveedor_id if proveedor_id != 'sin_proveedor' else None,
                    'proveedor': req.get('proveedor'),
                    'items': []
                }
            
            por_proveedor[proveedor_id]['items'].append({
                'item_id': req['item_id'],
                'item': req['item'],
                'cantidad': req['cantidad_a_pedir'],
                'unidad': req['unidad'],
                'precio_unitario': req['item'].costo_unitario_actual or 0
            })
        
        return por_proveedor
