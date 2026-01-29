"""
Lógica de negocio para gestión de inventario.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models import Inventario, Item, Factura, FacturaItem, Requerimiento, RequerimientoItem
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
    
    @staticmethod
    def obtener_inventario_completo_con_movimientos(db: Session) -> List[Dict]:
        """
        Obtiene el inventario completo con información de últimos movimientos.
        
        Returns:
            Lista de diccionarios con información completa del inventario
        """
        inventarios = db.query(Inventario).all()
        resultado = []
        
        for inv in inventarios:
            item_dict = inv.to_dict()
            
            # Obtener último ingreso (factura aprobada más reciente con este item)
            ultimo_ingreso = db.query(FacturaItem).join(Factura).filter(
                FacturaItem.item_id == inv.item_id,
                Factura.estado == 'aprobada',
                Factura.tipo == 'proveedor'
            ).order_by(desc(Factura.fecha_aprobacion)).first()
            
            # Obtener último egreso (requerimiento entregado más reciente con este item)
            ultimo_egreso = db.query(RequerimientoItem).join(Requerimiento).filter(
                RequerimientoItem.item_id == inv.item_id,
                Requerimiento.estado == 'entregado',
                RequerimientoItem.cantidad_entregada.isnot(None)
            ).order_by(desc(Requerimiento.fecha)).first()
            
            # Calcular stock disponible (cantidad_actual - cantidad_minima)
            stock_disponible = max(0, float(inv.cantidad_actual) - float(inv.cantidad_minima))
            
            item_dict['ultimo_ingreso'] = {
                'fecha': ultimo_ingreso.factura.fecha_aprobacion.isoformat() if ultimo_ingreso and ultimo_ingreso.factura.fecha_aprobacion else None,
                'cantidad': float(ultimo_ingreso.cantidad) if ultimo_ingreso else None,
                'factura_numero': ultimo_ingreso.factura.numero_factura if ultimo_ingreso else None,
                'proveedor': ultimo_ingreso.factura.proveedor.nombre if ultimo_ingreso and ultimo_ingreso.factura.proveedor else None,
            } if ultimo_ingreso else None
            
            item_dict['ultimo_egreso'] = {
                'fecha': ultimo_egreso.requerimiento.fecha.isoformat() if ultimo_egreso and ultimo_egreso.requerimiento.fecha else None,
                'cantidad': float(ultimo_egreso.cantidad_entregada) if ultimo_egreso and ultimo_egreso.cantidad_entregada else None,
                'requerimiento_id': ultimo_egreso.requerimiento_id if ultimo_egreso else None,
            } if ultimo_egreso else None
            
            item_dict['stock_disponible'] = stock_disponible
            item_dict['stock_seguridad'] = float(inv.cantidad_minima)
            
            resultado.append(item_dict)
        
        return resultado
    
    @staticmethod
    def obtener_resumen_dashboard(db: Session) -> Dict:
        """
        Obtiene un resumen tipo dashboard para el inventario.
        
        Returns:
            Diccionario con métricas del inventario
        """
        total_items = db.query(Inventario).count()
        items_stock_bajo = db.query(Inventario).filter(
            Inventario.cantidad_actual < Inventario.cantidad_minima
        ).count()
        
        # Calcular valor total del inventario
        inventarios = db.query(Inventario).all()
        valor_total = sum(
            float(inv.cantidad_actual) * float(inv.ultimo_costo_unitario or 0)
            for inv in inventarios
        )
        
        # Items críticos (stock muy bajo)
        items_criticos = db.query(Inventario).filter(
            Inventario.cantidad_actual < (Inventario.cantidad_minima * 0.5)
        ).count()
        
        return {
            'total_items': total_items,
            'items_stock_bajo': items_stock_bajo,
            'items_criticos': items_criticos,
            'items_stock_ok': total_items - items_stock_bajo,
            'valor_total_inventario': valor_total,
            'porcentaje_stock_bajo': round((items_stock_bajo / total_items * 100) if total_items > 0 else 0, 2),
        }