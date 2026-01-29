"""
Servicio para generación automática de pedidos basado en requerimientos.
Genera pedidos agrupados por proveedor y programa envío de notificaciones.
"""
from typing import List, Dict
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from models import PedidoCompra, PedidoCompraItem, Proveedor, Item
from models.pedido import EstadoPedido
from modules.planificacion.requerimientos import RequerimientosService
import threading
import time

class PedidosAutomaticosService:
    """Servicio para generación automática de pedidos."""
    
    @staticmethod
    def generar_pedidos_desde_programacion(
        db: Session,
        fecha_inicio: date = None,
        usuario_id: int = None
    ) -> List[PedidoCompra]:
        """
        Genera pedidos automáticamente basado en programación quincenal.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio (por defecto hoy)
            usuario_id: ID del usuario que genera los pedidos
            
        Returns:
            Lista de pedidos creados
        """
        if fecha_inicio is None:
            fecha_inicio = date.today()
        
        # Calcular requerimientos quincenales
        requerimientos_data = RequerimientosService.calcular_requerimientos_quincenales(
            db, fecha_inicio
        )
        
        # Agrupar por proveedor
        requerimientos_por_proveedor = RequerimientosService.agrupar_requerimientos_por_proveedor(
            requerimientos_data['requerimientos']
        )
        
        # Crear pedidos por proveedor
        pedidos_creados = []
        
        for proveedor_id_key, datos_proveedor in requerimientos_por_proveedor.items():
            # Saltar items sin proveedor
            if proveedor_id_key == 'sin_proveedor':
                continue
            
            proveedor_id = datos_proveedor['proveedor_id']
            proveedor = datos_proveedor['proveedor']
            
            # Verificar que el proveedor esté activo
            if not proveedor or not proveedor.activo:
                continue
            
            # Calcular fecha de entrega esperada (máximo tiempo de entrega de items)
            dias_maximos = 7  # Por defecto
            for item_data in datos_proveedor['items']:
                item = item_data['item']
                if item.tiempo_entrega_dias > dias_maximos:
                    dias_maximos = item.tiempo_entrega_dias
            
            fecha_entrega = datetime.now() + timedelta(days=dias_maximos)
            
            # Crear pedido
            pedido = PedidoCompra(
                proveedor_id=proveedor_id,
                fecha_entrega_esperada=fecha_entrega,
                estado=EstadoPedido.BORRADOR,
                creado_por=usuario_id,
                observaciones=f"Pedido automático generado desde programación quincenal ({requerimientos_data['fecha_inicio']} - {requerimientos_data['fecha_fin']})"
            )
            
            db.add(pedido)
            db.flush()
            
            # Agregar items al pedido
            total = 0
            for item_data in datos_proveedor['items']:
                item = item_data['item']
                cantidad = float(item_data['cantidad'])
                precio_unitario = float(item_data['precio_unitario'])
                subtotal = cantidad * precio_unitario
                
                pedido_item = PedidoCompraItem(
                    pedido_id=pedido.id,
                    item_id=item.id,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal
                )
                db.add(pedido_item)
                total += subtotal
            
            pedido.total = total
            pedidos_creados.append(pedido)
        
        db.commit()
        
        # Refrescar pedidos para obtener relaciones
        for pedido in pedidos_creados:
            db.refresh(pedido)
        
        return pedidos_creados
    
    @staticmethod
    def aprobar_y_programar_envio(
        db: Session,
        pedido_id: int,
        usuario_id: int = None
    ) -> PedidoCompra:
        """
        Aprueba un pedido y programa el envío automático 1 hora después.
        
        Args:
            db: Sesión de base de datos
            pedido_id: ID del pedido
            usuario_id: ID del usuario que aprueba
            
        Returns:
            Pedido aprobado
        """
        pedido = db.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido no encontrado")
        
        if pedido.estado != EstadoPedido.BORRADOR:
            raise ValueError("Solo se pueden aprobar pedidos en estado BORRADOR")
        
        # Cambiar estado a ENVIADO (aunque aún no se haya enviado físicamente)
        # El envío real se hará 1 hora después
        pedido.estado = EstadoPedido.ENVIADO
        
        # Programar envío 1 hora después
        # Usar threading para programar la tarea
        def enviar_pedido_después():
            time.sleep(3600)  # Esperar 1 hora (3600 segundos)
            PedidosAutomaticosService.enviar_pedido_a_proveedor(db, pedido_id)
        
        thread = threading.Thread(target=enviar_pedido_después)
        thread.daemon = True
        thread.start()
        
        db.commit()
        db.refresh(pedido)
        return pedido
    
    @staticmethod
    def enviar_pedido_a_proveedor(db: Session, pedido_id: int):
        """
        Envía el pedido al proveedor por WhatsApp y Email con PDF.
        Este método se ejecuta 1 hora después de aprobar el pedido.
        
        Args:
            db: Sesión de base de datos
            pedido_id: ID del pedido
        """
        from modules.logistica.pdf_pedidos import generar_pdf_pedido
        
        pedido = db.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()
        if not pedido:
            return
        
        proveedor = pedido.proveedor
        if not proveedor:
            return
        
        try:
            # Generar PDF del pedido
            pdf_path = generar_pdf_pedido(pedido)
            
            # Enviar por WhatsApp
            if proveedor.telefono:
                from modules.crm.notificaciones.whatsapp import whatsapp_service
                mensaje = (
                    f"📦 *Pedido #{pedido.id}*\n\n"
                    f"Proveedor: {proveedor.nombre}\n"
                    f"Total: ${float(pedido.total):,.2f}\n"
                    f"Fecha de entrega esperada: {pedido.fecha_entrega_esperada.strftime('%d/%m/%Y') if pedido.fecha_entrega_esperada else 'N/A'}\n\n"
                    f"Items:\n"
                )
                for item in pedido.items:
                    mensaje += f"• {item.item.nombre}: {item.cantidad} {item.item.unidad}\n"
                mensaje += f"\nSe adjunta PDF con detalles del pedido."
                
                # Enviar mensaje y PDF por WhatsApp
                whatsapp_service.enviar_mensaje(proveedor.telefono, mensaje)
                # TODO: Implementar envío de PDF por WhatsApp cuando esté disponible
            
            # Enviar por Email
            if proveedor.email:
                from modules.crm.notificaciones.email import email_service
                asunto = f"Pedido #{pedido.id} - {proveedor.nombre}"
                
                contenido_html = f"""
                <html>
                <body>
                    <h2>Pedido #{pedido.id}</h2>
                    <p><strong>Proveedor:</strong> {proveedor.nombre}</p>
                    <p><strong>Total:</strong> ${float(pedido.total):,.2f}</p>
                    <p><strong>Fecha de entrega esperada:</strong> {pedido.fecha_entrega_esperada.strftime('%d/%m/%Y') if pedido.fecha_entrega_esperada else 'N/A'}</p>
                    
                    <h3>Items:</h3>
                    <ul>
                """
                for item in pedido.items:
                    contenido_html += f"<li>{item.item.nombre}: {item.cantidad} {item.item.unidad} - ${float(item.subtotal):,.2f}</li>"
                
                contenido_html += """
                    </ul>
                    <p>Se adjunta PDF con detalles del pedido.</p>
                </body>
                </html>
                """
                
                # Enviar email con PDF adjunto
                email_service.enviar_email_con_adjunto(
                    proveedor.email,
                    asunto,
                    contenido_html,
                    pdf_path
                )
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar pedido {pedido_id} al proveedor: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
