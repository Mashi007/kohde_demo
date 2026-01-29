"""
Lógica de negocio para gestión de pedidos internos (bodega → cocina).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from models import PedidoInterno, PedidoInternoItem, Inventario, Item
from models.pedido_interno import EstadoPedidoInterno

class PedidoInternoService:
    """Servicio para gestión de pedidos internos."""
    
    @staticmethod
    def crear_pedido_interno(db: Session, datos: Dict) -> PedidoInterno:
        """
        Crea un nuevo pedido interno.
        
        Args:
            db: Sesión de base de datos
            datos: Datos del pedido (entregado_por_id, entregado_por_nombre, items, etc.)
            
        Returns:
            PedidoInterno creado
        """
        # Crear el pedido
        pedido = PedidoInterno(
            entregado_por_id=datos.get('entregado_por_id'),
            entregado_por_nombre=datos.get('entregado_por_nombre'),
            recibido_por_id=datos.get('recibido_por_id'),
            recibido_por_nombre=datos.get('recibido_por_nombre'),
            observaciones=datos.get('observaciones'),
            estado=EstadoPedidoInterno.PENDIENTE
        )
        
        db.add(pedido)
        db.flush()  # Para obtener el ID del pedido
        
        # Agregar items
        items_data = datos.get('items', [])
        for item_data in items_data:
            item = PedidoInternoItem(
                pedido_id=pedido.id,
                item_id=item_data['item_id'],
                cantidad=float(item_data['cantidad']),
                unidad=item_data.get('unidad')
            )
            db.add(item)
        
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def confirmar_entrega(db: Session, pedido_id: int, recibido_por_id: int, recibido_por_nombre: str) -> PedidoInterno:
        """
        Confirma la entrega de un pedido interno y actualiza el inventario.
        
        Args:
            db: Sesión de base de datos
            pedido_id: ID del pedido
            recibido_por_id: ID del usuario que recibe
            recibido_por_nombre: Nombre del usuario que recibe
            
        Returns:
            PedidoInterno actualizado
            
        Raises:
            ValueError: Si el pedido no existe o no está pendiente
        """
        pedido = db.query(PedidoInterno).filter(PedidoInterno.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido interno no encontrado")
        
        if pedido.estado != EstadoPedidoInterno.PENDIENTE:
            raise ValueError(f"El pedido ya está {pedido.estado.value}")
        
        # Verificar stock disponible antes de confirmar
        for item_pedido in pedido.items:
            inventario = db.query(Inventario).filter(Inventario.item_id == item_pedido.item_id).first()
            if not inventario:
                raise ValueError(f"No hay inventario registrado para el item {item_pedido.item.nombre}")
            
            cantidad_necesaria = float(item_pedido.cantidad)
            cantidad_disponible = float(inventario.cantidad_actual)
            
            if cantidad_disponible < cantidad_necesaria:
                raise ValueError(
                    f"Stock insuficiente para {item_pedido.item.nombre}. "
                    f"Disponible: {cantidad_disponible} {inventario.unidad}, "
                    f"Necesario: {cantidad_necesaria} {item_pedido.unidad or inventario.unidad}"
                )
        
        # Actualizar inventario (reducir stock de bodega)
        for item_pedido in pedido.items:
            inventario = db.query(Inventario).filter(Inventario.item_id == item_pedido.item_id).first()
            cantidad_necesaria = float(item_pedido.cantidad)
            
            # Reducir cantidad actual
            inventario.cantidad_actual = float(inventario.cantidad_actual) - cantidad_necesaria
            inventario.ultima_actualizacion = datetime.utcnow()
        
        # Actualizar pedido
        pedido.estado = EstadoPedidoInterno.ENTREGADO
        pedido.fecha_entrega = datetime.utcnow()
        pedido.recibido_por_id = recibido_por_id
        pedido.recibido_por_nombre = recibido_por_nombre
        
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def cancelar_pedido(db: Session, pedido_id: int) -> PedidoInterno:
        """
        Cancela un pedido interno pendiente.
        
        Args:
            db: Sesión de base de datos
            pedido_id: ID del pedido
            
        Returns:
            PedidoInterno cancelado
            
        Raises:
            ValueError: Si el pedido no existe o ya fue entregado
        """
        pedido = db.query(PedidoInterno).filter(PedidoInterno.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido interno no encontrado")
        
        if pedido.estado == EstadoPedidoInterno.ENTREGADO:
            raise ValueError("No se puede cancelar un pedido ya entregado")
        
        pedido.estado = EstadoPedidoInterno.CANCELADO
        
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def listar_pedidos_internos(
        db: Session,
        estado: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PedidoInterno]:
        """
        Lista pedidos internos con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            estado: Filtrar por estado (pendiente, entregado, cancelado)
            fecha_desde: Filtrar desde fecha
            fecha_hasta: Filtrar hasta fecha
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de PedidoInterno
        """
        query = db.query(PedidoInterno)
        
        if estado:
            try:
                estado_enum = EstadoPedidoInterno[estado.upper()]
                query = query.filter(PedidoInterno.estado == estado_enum)
            except KeyError:
                pass
        
        if fecha_desde:
            query = query.filter(PedidoInterno.fecha_pedido >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(PedidoInterno.fecha_pedido <= fecha_hasta)
        
        return query.order_by(desc(PedidoInterno.fecha_pedido)).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_pedido_interno(db: Session, pedido_id: int) -> Optional[PedidoInterno]:
        """Obtiene un pedido interno por ID."""
        return db.query(PedidoInterno).filter(PedidoInterno.id == pedido_id).first()
