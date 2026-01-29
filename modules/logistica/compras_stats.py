"""
Servicio para estadísticas y resúmenes de compras.
Incluye análisis por item, por proveedor, y relación con inventario y programación.
"""
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from models import (
    PedidoCompra, PedidoCompraItem, Factura, FacturaItem,
    Inventario, Item, Proveedor, ProgramacionMenu
)
from models.pedido import EstadoPedido
from models.factura import EstadoFactura, TipoFactura

class ComprasStatsService:
    """Servicio para estadísticas de compras."""
    
    @staticmethod
    def obtener_resumen_general(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Dict:
        """
        Obtiene un resumen general de compras.
        
        Args:
            db: Sesión de base de datos
            fecha_desde: Fecha de inicio del período
            fecha_hasta: Fecha de fin del período
            
        Returns:
            Diccionario con resumen general
        """
        if fecha_desde is None:
            fecha_desde = date.today() - timedelta(days=30)  # Últimos 30 días por defecto
        if fecha_hasta is None:
            fecha_hasta = date.today()
        
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
        
        # Total de pedidos
        total_pedidos = db.query(PedidoCompra).filter(
            and_(
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).count()
        
        # Pedidos por estado
        pedidos_por_estado = db.query(
            PedidoCompra.estado,
            func.count(PedidoCompra.id).label('cantidad')
        ).filter(
            and_(
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).group_by(PedidoCompra.estado).all()
        
        # Total de facturas de proveedores
        total_facturas = db.query(Factura).filter(
            and_(
                Factura.tipo == TipoFactura.PROVEEDOR,
                Factura.fecha_recepcion >= fecha_desde_dt,
                Factura.fecha_recepcion <= fecha_hasta_dt
            )
        ).count()
        
        # Total gastado en pedidos recibidos
        total_gastado_pedidos = db.query(
            func.sum(PedidoCompra.total)
        ).filter(
            and_(
                PedidoCompra.estado == EstadoPedido.RECIBIDO,
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).scalar() or 0
        
        # Total gastado en facturas aprobadas
        total_gastado_facturas = db.query(
            func.sum(Factura.total)
        ).filter(
            and_(
                Factura.tipo == TipoFactura.PROVEEDOR,
                Factura.estado == EstadoFactura.APROBADA,
                Factura.fecha_recepcion >= fecha_desde_dt,
                Factura.fecha_recepcion <= fecha_hasta_dt
            )
        ).scalar() or 0
        
        # Total gastado (pedidos + facturas)
        total_gastado = float(total_gastado_pedidos) + float(total_gastado_facturas)
        
        # Pedidos pendientes de aprobación
        pedidos_pendientes = db.query(PedidoCompra).filter(
            PedidoCompra.estado == EstadoPedido.BORRADOR
        ).count()
        
        return {
            'periodo': {
                'fecha_desde': fecha_desde.isoformat(),
                'fecha_hasta': fecha_hasta.isoformat()
            },
            'resumen': {
                'total_pedidos': total_pedidos,
                'total_facturas': total_facturas,
                'total_gastado': total_gastado,
                'total_gastado_pedidos': float(total_gastado_pedidos),
                'total_gastado_facturas': float(total_gastado_facturas),
                'pedidos_pendientes': pedidos_pendientes
            },
            'pedidos_por_estado': {
                estado.value if isinstance(estado, EstadoPedido) else estado: cantidad
                for estado, cantidad in pedidos_por_estado
            }
        }
    
    @staticmethod
    def obtener_resumen_por_item(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 20
    ) -> List[Dict]:
        """
        Obtiene resumen de compras agrupado por item.
        
        Args:
            db: Sesión de base de datos
            fecha_desde: Fecha de inicio del período
            fecha_hasta: Fecha de fin del período
            limite: Número máximo de items a retornar
            
        Returns:
            Lista de items con estadísticas de compra
        """
        if fecha_desde is None:
            fecha_desde = date.today() - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = date.today()
        
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
        
        # Estadísticas desde pedidos recibidos
        stats_pedidos = db.query(
            PedidoCompraItem.item_id,
            func.sum(PedidoCompraItem.cantidad).label('cantidad_total'),
            func.sum(PedidoCompraItem.subtotal).label('total_gastado'),
            func.avg(PedidoCompraItem.precio_unitario).label('precio_promedio'),
            func.count(PedidoCompraItem.id).label('veces_comprado')
        ).join(
            PedidoCompra, PedidoCompraItem.pedido_id == PedidoCompra.id
        ).filter(
            and_(
                PedidoCompra.estado == EstadoPedido.RECIBIDO,
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).group_by(PedidoCompraItem.item_id).subquery()
        
        # Estadísticas desde facturas aprobadas
        stats_facturas = db.query(
            FacturaItem.item_id,
            func.sum(FacturaItem.cantidad_aprobada).label('cantidad_total'),
            func.sum(FacturaItem.subtotal).label('total_gastado'),
            func.avg(FacturaItem.precio_unitario).label('precio_promedio'),
            func.count(FacturaItem.id).label('veces_comprado')
        ).join(
            Factura, FacturaItem.factura_id == Factura.id
        ).filter(
            and_(
                Factura.tipo == TipoFactura.PROVEEDOR,
                Factura.estado == EstadoFactura.APROBADA,
                Factura.fecha_recepcion >= fecha_desde_dt,
                Factura.fecha_recepcion <= fecha_hasta_dt,
                FacturaItem.item_id.isnot(None)
            )
        ).group_by(FacturaItem.item_id).subquery()
        
        # Combinar estadísticas de pedidos y facturas
        # Usar UNION ALL y luego agrupar
        resultado = []
        
        # Obtener items únicos de ambas fuentes
        item_ids_pedidos = db.query(stats_pedidos.c.item_id).all()
        item_ids_facturas = db.query(stats_facturas.c.item_id).all()
        item_ids_unicos = set([r[0] for r in item_ids_pedidos] + [r[0] for r in item_ids_facturas if r[0]])
        
        for item_id in item_ids_unicos:
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                continue
            
            # Obtener stats de pedidos
            pedido_stats = db.query(stats_pedidos).filter(
                stats_pedidos.c.item_id == item_id
            ).first()
            
            # Obtener stats de facturas
            factura_stats = db.query(stats_facturas).filter(
                stats_facturas.c.item_id == item_id
            ).first()
            
            cantidad_total = 0
            total_gastado = 0
            veces_comprado = 0
            precio_promedio = 0
            
            if pedido_stats:
                cantidad_total += float(pedido_stats.cantidad_total or 0)
                total_gastado += float(pedido_stats.total_gastado or 0)
                veces_comprado += int(pedido_stats.veces_comprado or 0)
            
            if factura_stats:
                cantidad_total += float(factura_stats.cantidad_total or 0)
                total_gastado += float(factura_stats.total_gastado or 0)
                veces_comprado += int(factura_stats.veces_comprado or 0)
            
            # Calcular precio promedio ponderado
            if cantidad_total > 0:
                precio_promedio = total_gastado / cantidad_total
            
            # Obtener inventario actual
            inventario = db.query(Inventario).filter(
                Inventario.item_id == item_id
            ).first()
            
            resultado.append({
                'item_id': item_id,
                'item': item.to_dict(),
                'cantidad_total_comprada': cantidad_total,
                'total_gastado': total_gastado,
                'veces_comprado': veces_comprado,
                'precio_promedio': precio_promedio,
                'unidad': item.unidad,
                'inventario_actual': float(inventario.cantidad_actual) if inventario else 0,
                'inventario_minimo': float(inventario.cantidad_minima) if inventario else 0,
                'proveedor': item.proveedor_autorizado.to_dict() if item.proveedor_autorizado else None
            })
        
        # Ordenar por total gastado descendente
        resultado.sort(key=lambda x: x['total_gastado'], reverse=True)
        
        return resultado[:limite]
    
    @staticmethod
    def obtener_resumen_por_proveedor(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        limite: int = 20
    ) -> List[Dict]:
        """
        Obtiene resumen de compras agrupado por proveedor.
        
        Args:
            db: Sesión de base de datos
            fecha_desde: Fecha de inicio del período
            fecha_hasta: Fecha de fin del período
            limite: Número máximo de proveedores a retornar
            
        Returns:
            Lista de proveedores con estadísticas de compra
        """
        if fecha_desde is None:
            fecha_desde = date.today() - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = date.today()
        
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
        
        # Estadísticas desde pedidos recibidos
        stats_pedidos = db.query(
            PedidoCompra.proveedor_id,
            func.count(PedidoCompra.id).label('total_pedidos'),
            func.sum(PedidoCompra.total).label('total_gastado'),
            func.avg(PedidoCompra.total).label('promedio_pedido')
        ).filter(
            and_(
                PedidoCompra.estado == EstadoPedido.RECIBIDO,
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).group_by(PedidoCompra.proveedor_id).subquery()
        
        # Estadísticas desde facturas aprobadas
        stats_facturas = db.query(
            Factura.proveedor_id,
            func.count(Factura.id).label('total_facturas'),
            func.sum(Factura.total).label('total_gastado'),
            func.avg(Factura.total).label('promedio_factura')
        ).filter(
            and_(
                Factura.tipo == TipoFactura.PROVEEDOR,
                Factura.estado == EstadoFactura.APROBADA,
                Factura.fecha_recepcion >= fecha_desde_dt,
                Factura.fecha_recepcion <= fecha_hasta_dt
            )
        ).group_by(Factura.proveedor_id).subquery()
        
        # Obtener proveedores únicos
        proveedor_ids_pedidos = db.query(stats_pedidos.c.proveedor_id).all()
        proveedor_ids_facturas = db.query(stats_facturas.c.proveedor_id).all()
        proveedor_ids_unicos = set(
            [r[0] for r in proveedor_ids_pedidos] + 
            [r[0] for r in proveedor_ids_facturas if r[0]]
        )
        
        resultado = []
        
        for proveedor_id in proveedor_ids_unicos:
            proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
            if not proveedor:
                continue
            
            # Obtener stats de pedidos
            pedido_stats = db.query(stats_pedidos).filter(
                stats_pedidos.c.proveedor_id == proveedor_id
            ).first()
            
            # Obtener stats de facturas
            factura_stats = db.query(stats_facturas).filter(
                stats_facturas.c.proveedor_id == proveedor_id
            ).first()
            
            total_pedidos = int(pedido_stats.total_pedidos) if pedido_stats else 0
            total_facturas = int(factura_stats.total_facturas) if factura_stats else 0
            total_gastado_pedidos = float(pedido_stats.total_gastado) if pedido_stats and pedido_stats.total_gastado else 0
            total_gastado_facturas = float(factura_stats.total_gastado) if factura_stats and factura_stats.total_gastado else 0
            total_gastado = total_gastado_pedidos + total_gastado_facturas
            
            promedio_pedido = float(pedido_stats.promedio_pedido) if pedido_stats and pedido_stats.promedio_pedido else 0
            promedio_factura = float(factura_stats.promedio_factura) if factura_stats and factura_stats.promedio_factura else 0
            
            # Obtener items que provee
            items_proveedor = db.query(Item).filter(
                Item.proveedor_autorizado_id == proveedor_id,
                Item.activo == True
            ).count()
            
            resultado.append({
                'proveedor_id': proveedor_id,
                'proveedor': proveedor.to_dict(),
                'total_pedidos': total_pedidos,
                'total_facturas': total_facturas,
                'total_gastado': total_gastado,
                'total_gastado_pedidos': total_gastado_pedidos,
                'total_gastado_facturas': total_gastado_facturas,
                'promedio_pedido': promedio_pedido,
                'promedio_factura': promedio_factura,
                'items_que_provee': items_proveedor,
                'activo': proveedor.activo
            })
        
        # Ordenar por total gastado descendente
        resultado.sort(key=lambda x: x['total_gastado'], reverse=True)
        
        return resultado[:limite]
    
    @staticmethod
    def obtener_compras_por_proceso(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Dict:
        """
        Obtiene estadísticas de compras relacionadas con procesos de inventario y programación.
        
        Args:
            db: Sesión de base de datos
            fecha_desde: Fecha de inicio del período
            fecha_hasta: Fecha de fin del período
            
        Returns:
            Diccionario con estadísticas por proceso
        """
        if fecha_desde is None:
            fecha_desde = date.today() - timedelta(days=30)
        if fecha_hasta is None:
            fecha_hasta = date.today()
        
        fecha_desde_dt = datetime.combine(fecha_desde, datetime.min.time())
        fecha_hasta_dt = datetime.combine(fecha_hasta, datetime.max.time())
        
        # Pedidos generados automáticamente (desde programación)
        pedidos_automaticos = db.query(PedidoCompra).filter(
            and_(
                PedidoCompra.observaciones.like('%automático%'),
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).count()
        
        # Total de pedidos automáticos
        total_pedidos_automaticos = db.query(
            func.sum(PedidoCompra.total)
        ).filter(
            and_(
                PedidoCompra.observaciones.like('%automático%'),
                PedidoCompra.estado == EstadoPedido.RECIBIDO,
                PedidoCompra.fecha_pedido >= fecha_desde_dt,
                PedidoCompra.fecha_pedido <= fecha_hasta_dt
            )
        ).scalar() or 0
        
        # Programaciones realizadas en el período
        programaciones = db.query(ProgramacionMenu).filter(
            and_(
                ProgramacionMenu.fecha >= fecha_desde,
                ProgramacionMenu.fecha <= fecha_hasta
            )
        ).count()
        
        # Items con inventario bajo (por debajo del mínimo)
        items_bajo_stock = db.query(Inventario).filter(
            Inventario.cantidad_actual < Inventario.cantidad_minima
        ).count()
        
        # Total de items en inventario
        total_items_inventario = db.query(Inventario).count()
        
        return {
            'pedidos_automaticos': {
                'cantidad': pedidos_automaticos,
                'total_gastado': float(total_pedidos_automaticos)
            },
            'programaciones': {
                'cantidad': programaciones
            },
            'inventario': {
                'items_bajo_stock': items_bajo_stock,
                'total_items': total_items_inventario,
                'porcentaje_bajo_stock': (items_bajo_stock / total_items_inventario * 100) if total_items_inventario > 0 else 0
            }
        }
