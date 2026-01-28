"""
Lógica de negocio para gestión de inventario.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models import Inventario, Item
from utils.helpers import verificar_stock_suficiente

class InventarioService:
    """Servicio para gestión de inventario."""
    
    @staticmethod
    def obtener_inventario(db: Session, item_id: Optional[int] = None) -> List[Inventario]:
        """
        Obtiene el inventario completo o de un item específico.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item (opcional)
            
        Returns:
            Lista de registros de inventario
        """
        query = db.query(Inventario)
        
        if item_id:
            query = query.filter(Inventario.item_id == item_id)
        
        return query.all()
    
    @staticmethod
    def obtener_stock_bajo(db: Session) -> List[Dict]:
        """
        Obtiene items con stock bajo (cantidad_actual < cantidad_minima).
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de items con stock bajo
        """
        items_bajo_stock = db.query(Inventario).filter(
            Inventario.cantidad_actual < Inventario.cantidad_minima
        ).all()
        
        resultado = []
        for inv in items_bajo_stock:
            resultado.append({
                'item_id': inv.item_id,
                'nombre': inv.item.nombre if inv.item else 'N/A',
                'cantidad_actual': float(inv.cantidad_actual),
                'cantidad_minima': float(inv.cantidad_minima),
                'unidad': inv.unidad,
                'ubicacion': inv.ubicacion
            })
        
        return resultado
    
    @staticmethod
    def actualizar_stock(
        db: Session,
        item_id: int,
        cantidad: float,
        operacion: str = 'entrada'  # 'entrada' o 'salida'
    ) -> Inventario:
        """
        Actualiza el stock de un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            cantidad: Cantidad a agregar o restar
            operacion: 'entrada' o 'salida'
            
        Returns:
            Inventario actualizado
        """
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        
        if not inventario:
            # Crear registro si no existe
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                raise ValueError("Item no encontrado")
            
            inventario = Inventario(
                item_id=item_id,
                cantidad_actual=0,
                unidad=item.unidad
            )
            db.add(inventario)
        
        # Actualizar cantidad
        if operacion == 'entrada':
            inventario.cantidad_actual += cantidad
        elif operacion == 'salida':
            inventario.cantidad_actual -= cantidad
            if inventario.cantidad_actual < 0:
                raise ValueError("No hay suficiente stock")
        else:
            raise ValueError("Operación inválida")
        
        db.commit()
        db.refresh(inventario)
        return inventario
    
    @staticmethod
    def verificar_disponibilidad(
        db: Session,
        item_id: int,
        cantidad_necesaria: float
    ) -> Dict:
        """
        Verifica si hay stock disponible para una cantidad necesaria.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            cantidad_necesaria: Cantidad necesaria
            
        Returns:
            Diccionario con resultado de la verificación
        """
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        
        if not inventario:
            return {
                'suficiente': False,
                'cantidad_disponible': 0,
                'cantidad_faltante': cantidad_necesaria,
                'cantidad_necesaria': cantidad_necesaria,
                'cantidad_actual': 0,
                'cantidad_minima': 0,
            }
        
        return verificar_stock_suficiente(
            cantidad_necesaria,
            float(inventario.cantidad_actual),
            float(inventario.cantidad_minima)
        )
