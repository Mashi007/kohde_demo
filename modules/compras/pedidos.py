"""
Lógica de negocio para gestión de pedidos de compra.
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from models import PedidoCompra, PedidoCompraItem, Proveedor, Item
from models.item import Item as ItemModel
from models.pedido import EstadoPedido
from utils.helpers import agrupar_items_por_proveedor, obtener_fecha_entrega_esperada
from modules.notificaciones.whatsapp import whatsapp_service
from modules.notificaciones.email import email_service

class PedidoCompraService:
    """Servicio para gestión de pedidos de compra."""
    
    @staticmethod
    def crear_pedido(db: Session, datos: Dict) -> PedidoCompra:
        """
        Crea un nuevo pedido de compra.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del pedido
            
        Returns:
            Pedido creado
        """
        pedido = PedidoCompra(
            proveedor_id=datos['proveedor_id'],
            fecha_entrega_esperada=datos.get('fecha_entrega_esperada'),
            estado=EstadoPedido.BORRADOR,
            creado_por=datos.get('creado_por'),
            observaciones=datos.get('observaciones')
        )
        
        db.add(pedido)
        db.flush()  # Para obtener el ID
        
        # Crear items del pedido
        total = 0
        for item_data in datos.get('items', []):
            item = db.query(Item).filter(Item.id == item_data['item_id']).first()
            if not item:
                raise ValueError(f"Item {item_data['item_id']} no encontrado")
            
            precio = float(item_data.get('precio_unitario', item.costo_unitario_actual or 0))
            cantidad = float(item_data['cantidad'])
            subtotal = precio * cantidad
            
            pedido_item = PedidoCompraItem(
                pedido_id=pedido.id,
                item_id=item.id,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=subtotal
            )
            db.add(pedido_item)
            total += subtotal
        
        pedido.total = total
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def generar_pedido_automatico(
        db: Session,
        items_necesarios: List[Dict],
        usuario_id: int
    ) -> List[PedidoCompra]:
        """
        Genera pedidos automáticos agrupados por proveedor.
        
        Args:
            db: Sesión de base de datos
            items_necesarios: Lista de items con cantidad necesaria
            usuario_id: ID del usuario que genera el pedido
            
        Returns:
            Lista de pedidos creados
        """
        # Agrupar items por proveedor
        items_por_proveedor = {}
        
        for item_data in items_necesarios:
            item_id = item_data['item_id']
            cantidad = item_data['cantidad']
            
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item or not item.proveedor_autorizado_id:
                continue  # Saltar items sin proveedor autorizado
            
            proveedor_id = item.proveedor_autorizado_id
            
            if proveedor_id not in items_por_proveedor:
                items_por_proveedor[proveedor_id] = []
            
            items_por_proveedor[proveedor_id].append({
                'item_id': item_id,
                'cantidad': cantidad,
                'precio_unitario': item.costo_unitario_actual or 0
            })
        
        # Crear pedido por cada proveedor
        pedidos_creados = []
        
        for proveedor_id, items in items_por_proveedor.items():
            proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
            if not proveedor:
                continue
            
            # Calcular fecha de entrega esperada
            dias_maximos = max([
                db.query(ItemModel).filter(ItemModel.id == item['item_id']).first().tiempo_entrega_dias
                for item in items
            ])
            fecha_entrega = obtener_fecha_entrega_esperada(dias_maximos)
            
            pedido = PedidoCompraService.crear_pedido(db, {
                'proveedor_id': proveedor_id,
                'fecha_entrega_esperada': fecha_entrega,
                'creado_por': usuario_id,
                'items': items
            })
            
            pedidos_creados.append(pedido)
            
            # Notificar a comprador
            try:
                # Aquí deberías obtener el teléfono del comprador desde usuarios
                # Por ahora, usar el teléfono del proveedor como ejemplo
                if proveedor.telefono:
                    whatsapp_service.notificar_pedido_generado(
                        proveedor.telefono,
                        {
                            'proveedor': proveedor.nombre,
                            'total': float(pedido.total),
                            'cantidad_items': len(items)
                        }
                    )
            except Exception as e:
                print(f"Error al enviar notificación: {e}")
        
        return pedidos_creados
    
    @staticmethod
    def enviar_pedido(db: Session, pedido_id: int) -> PedidoCompra:
        """
        Envía un pedido al proveedor (cambia estado a ENVIADO).
        
        Args:
            db: Sesión de base de datos
            pedido_id: ID del pedido
            
        Returns:
            Pedido enviado
        """
        pedido = db.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido no encontrado")
        
        if pedido.estado != EstadoPedido.BORRADOR:
            raise ValueError("Solo se pueden enviar pedidos en estado BORRADOR")
        
        pedido.estado = EstadoPedido.ENVIADO
        
        # Enviar por WhatsApp/Email al proveedor
        try:
            proveedor = pedido.proveedor
            if proveedor.telefono:
                mensaje = f"Pedido #{pedido.id}\nTotal: ${pedido.total:,.2f}\n"
                mensaje += "Items:\n"
                for item in pedido.items:
                    mensaje += f"- {item.item.nombre}: {item.cantidad} {item.item.unidad}\n"
                
                whatsapp_service.enviar_mensaje(proveedor.telefono, mensaje)
            
            if proveedor.email:
                email_service.enviar_email(
                    proveedor.email,
                    f"Pedido #{pedido.id}",
                    f"<h2>Pedido #{pedido.id}</h2><p>Total: ${pedido.total:,.2f}</p>"
                )
        except Exception as e:
            print(f"Error al enviar pedido al proveedor: {e}")
        
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def listar_pedidos(
        db: Session,
        proveedor_id: Optional[int] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PedidoCompra]:
        """
        Lista pedidos con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            proveedor_id: Filtrar por proveedor
            estado: Filtrar por estado
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de pedidos
        """
        query = db.query(PedidoCompra)
        
        if proveedor_id:
            query = query.filter(PedidoCompra.proveedor_id == proveedor_id)
        
        if estado:
            query = query.filter(PedidoCompra.estado == EstadoPedido[estado.upper()])
        
        return query.order_by(PedidoCompra.fecha_pedido.desc()).offset(skip).limit(limit).all()
