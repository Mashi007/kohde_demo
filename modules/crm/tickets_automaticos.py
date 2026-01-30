"""
Servicio para generación automática de tickets basado en límites y reglas de negocio.
"""
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import (
    Ticket, Charola, Merma, ProgramacionMenu, Inventario,
    Proveedor, PedidoCompra, Item
)
from models.ticket import TipoTicket, EstadoTicket, PrioridadTicket
from models.pedido import EstadoPedido
from models.programacion import TiempoComida

class TicketsAutomaticosService:
    """Servicio para generación automática de tickets."""
    
    # Horarios de servicio (hora local)
    HORARIOS_SERVICIO = {
        TiempoComida.DESAYUNO: time(7, 0),   # 7:00 AM
        TiempoComida.ALMUERZO: time(13, 0),  # 1:00 PM
        TiempoComida.CENA: time(19, 0),      # 7:00 PM
    }
    
    # Tiempo límite para reportar (2 horas después del servicio)
    TIEMPO_LIMITE_REPORTE = timedelta(hours=2)
    
    @staticmethod
    def verificar_charolas_vs_planificacion(db: Session, fecha: date = None) -> List[Ticket]:
        """
        Verifica charolas servidas vs planificadas y genera tickets si hay desviaciones.
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha a verificar (por defecto hoy)
            
        Returns:
            Lista de tickets generados
        """
        if fecha is None:
            fecha = date.today()
        
        tickets_generados = []
        
        # Obtener todas las programaciones que incluyan esta fecha en su rango
        programaciones = db.query(ProgramacionMenu).filter(
            and_(
                ProgramacionMenu.fecha_desde <= fecha,
                ProgramacionMenu.fecha_hasta >= fecha
            )
        ).all()
        
        for programacion in programaciones:
            # Obtener charolas servidas para este servicio
            charolas_servidas = db.query(Charola).filter(
                and_(
                    func.date(Charola.fecha_servicio) == fecha,
                    Charola.tiempo_comida == programacion.tiempo_comida.value,
                    Charola.ubicacion == programacion.ubicacion
                )
            ).all()
            
            cantidad_servida = len(charolas_servidas)
            cantidad_planificada = programacion.charolas_planificadas
            
            # Verificar si ya existe un ticket para esta programación
            ticket_existente = db.query(Ticket).filter(
                and_(
                    Ticket.programacion_id == programacion.id,
                    Ticket.origen_modulo == 'charola',
                    Ticket.auto_generado == 'true',
                    func.date(Ticket.fecha_creacion) == fecha
                )
            ).first()
            
            if ticket_existente:
                continue
            
            # Generar ticket si hay desviación
            if cantidad_planificada > 0:
                diferencia = cantidad_servida - cantidad_planificada
                porcentaje_desviacion = (diferencia / cantidad_planificada) * 100
                
                # Si la diferencia es significativa (>10% o >5 charolas)
                if abs(diferencia) > max(5, cantidad_planificada * 0.1):
                    tipo_ticket = TipoTicket.CONSULTA if diferencia < 0 else TipoTicket.QUEJA
                    prioridad = PrioridadTicket.ALTA if abs(porcentaje_desviacion) > 20 else PrioridadTicket.MEDIA
                    
                    asunto = f"Desviación en charolas - {programacion.tiempo_comida.value.capitalize()}"
                    descripcion = (
                        f"Desviación detectada en el servicio de {programacion.tiempo_comida.value} "
                        f"del {fecha.strftime('%d/%m/%Y')} en {programacion.ubicacion}.\n\n"
                        f"Charolas planificadas: {cantidad_planificada}\n"
                        f"Charolas servidas: {cantidad_servida}\n"
                        f"Diferencia: {diferencia:+d} ({porcentaje_desviacion:+.1f}%)\n\n"
                        f"Programación ID: {programacion.id}"
                    )
                    
                    ticket = Ticket(
                        cliente_id=0,  # Tickets automáticos usan cliente dummy id=0
                        tipo=tipo_ticket,
                        asunto=asunto,
                        descripcion=descripcion,
                        estado=EstadoTicket.ABIERTO,
                        prioridad=prioridad,
                        programacion_id=programacion.id,
                        origen_modulo='charola',
                        auto_generado='true'
                    )
                    
                    db.add(ticket)
                    tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def verificar_mermas_limites(db: Session, fecha: date = None) -> List[Ticket]:
        """
        Verifica mermas contra límites estándar y genera tickets si se sobrepasan.
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha a verificar (por defecto hoy)
            
        Returns:
            Lista de tickets generados
        """
        if fecha is None:
            fecha = date.today()
        
        tickets_generados = []
        
        # Obtener todas las mermas del día
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())
        
        mermas = db.query(Merma).filter(
            and_(
                Merma.fecha_merma >= fecha_inicio,
                Merma.fecha_merma <= fecha_fin
            )
        ).all()
        
        # Agrupar mermas por item
        mermas_por_item = {}
        for merma in mermas:
            if merma.item_id not in mermas_por_item:
                mermas_por_item[merma.item_id] = []
            mermas_por_item[merma.item_id].append(merma)
        
        for item_id, mermas_item in mermas_por_item.items():
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                continue
            
            # Calcular total de merma del día
            total_cantidad = sum(float(m.cantidad) for m in mermas_item)
            total_costo = sum(float(m.costo_total) for m in mermas_item)
            
            # Obtener inventario del item
            inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
            
            # Límites estándar (configurables)
            # Porcentaje estándar: 5% del inventario actual o mínimo
            # Absoluto: 10 unidades o 5% del mínimo, lo que sea mayor
            if inventario:
                cantidad_referencia = max(
                    float(inventario.cantidad_actual),
                    float(inventario.cantidad_minima)
                )
                limite_porcentaje = cantidad_referencia * 0.05  # 5%
                limite_absoluto = max(10, cantidad_referencia * 0.05)
            else:
                limite_porcentaje = 10
                limite_absoluto = 10
            
            # Verificar si ya existe un ticket para este item en esta fecha
            ticket_existente = db.query(Ticket).filter(
                and_(
                    Ticket.merma_id.in_([m.id for m in mermas_item]),
                    Ticket.origen_modulo == 'merma',
                    Ticket.auto_generado == 'true',
                    func.date(Ticket.fecha_creacion) == fecha
                )
            ).first()
            
            if ticket_existente:
                continue
            
            # Generar ticket si se sobrepasa algún límite
            porcentaje_merma = (total_cantidad / cantidad_referencia * 100) if inventario and cantidad_referencia > 0 else 0
            
            if total_cantidad > limite_absoluto or porcentaje_merma > 5:
                asunto = f"Merma excesiva - {item.nombre}"
                descripcion = (
                    f"Merma excesiva detectada para el item '{item.nombre}' "
                    f"el {fecha.strftime('%d/%m/%Y')}.\n\n"
                    f"Cantidad de merma: {total_cantidad:.2f} {item.unidad}\n"
                    f"Costo total: ${total_costo:.2f}\n"
                    f"Límite absoluto: {limite_absoluto:.2f} {item.unidad}\n"
                    f"Porcentaje vs referencia: {porcentaje_merma:.2f}%\n\n"
                    f"Items de merma:\n"
                )
                
                for merma in mermas_item:
                    descripcion += (
                        f"- {merma.tipo.value}: {float(merma.cantidad):.2f} {merma.unidad} "
                        f"(${float(merma.costo_total):.2f}) - {merma.motivo or 'Sin motivo'}\n"
                    )
                
                descripcion += f"\nMerma ID principal: {mermas_item[0].id}"
                
                ticket = Ticket(
                    cliente_id=None,  # Tickets automáticos no tienen cliente asociado
                    tipo=TipoTicket.QUEJA,
                    asunto=asunto,
                    descripcion=descripcion,
                    estado=EstadoTicket.ABIERTO,
                    prioridad=PrioridadTicket.ALTA if porcentaje_merma > 10 else PrioridadTicket.MEDIA,
                    merma_id=mermas_item[0].id,
                    origen_modulo='merma',
                    auto_generado='true'
                )
                
                db.add(ticket)
                tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def verificar_inventario_seguridad(db: Session) -> List[Ticket]:
        """
        Verifica inventario bajo el mínimo de seguridad y genera tickets.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de tickets generados
        """
        tickets_generados = []
        
        # Obtener items con inventario bajo el mínimo
        items_bajo_stock = db.query(Inventario).filter(
            Inventario.cantidad_actual < Inventario.cantidad_minima
        ).all()
        
        for inventario in items_bajo_stock:
            # Verificar si ya existe un ticket abierto para este inventario
            ticket_existente = db.query(Ticket).filter(
                and_(
                    Ticket.inventario_id == inventario.id,
                    Ticket.origen_modulo == 'inventario',
                    Ticket.estado.in_([EstadoTicket.ABIERTO, EstadoTicket.EN_PROCESO])
                )
            ).first()
            
            if ticket_existente:
                continue
            
            item = inventario.item
            diferencia = float(inventario.cantidad_minima) - float(inventario.cantidad_actual)
            porcentaje_faltante = (diferencia / float(inventario.cantidad_minima)) * 100 if inventario.cantidad_minima > 0 else 0
            
            asunto = f"Inventario bajo mínimo - {item.nombre}"
            descripcion = (
                f"El inventario del item '{item.nombre}' está por debajo del mínimo de seguridad.\n\n"
                f"Cantidad actual: {float(inventario.cantidad_actual):.2f} {inventario.unidad}\n"
                f"Cantidad mínima: {float(inventario.cantidad_minima):.2f} {inventario.unidad}\n"
                f"Faltante: {diferencia:.2f} {inventario.unidad} ({porcentaje_faltante:.1f}%)\n\n"
                f"Inventario ID: {inventario.id}\n"
                f"Item ID: {item.id}"
            )
            
            if item.proveedor_autorizado:
                descripcion += f"\nProveedor autorizado: {item.proveedor_autorizado.nombre}"
            
            ticket = Ticket(
                cliente_id=None,  # Tickets automáticos no tienen cliente asociado
                tipo=TipoTicket.CONSULTA,
                asunto=asunto,
                descripcion=descripcion,
                estado=EstadoTicket.ABIERTO,
                prioridad=PrioridadTicket.URGENTE if porcentaje_faltante > 50 else PrioridadTicket.ALTA,
                inventario_id=inventario.id,
                proveedor_id=item.proveedor_autorizado_id if item.proveedor_autorizado else None,
                origen_modulo='inventario',
                auto_generado='true'
            )
            
            db.add(ticket)
            tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def verificar_programacion_faltante(db: Session, fecha: date = None) -> List[Ticket]:
        """
        Verifica si falta programación para el día y genera tickets de consulta.
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha a verificar (por defecto hoy)
            
        Returns:
            Lista de tickets generados
        """
        if fecha is None:
            fecha = date.today()
        
        tickets_generados = []
        
        # Verificar si hay programación para cada servicio del día
        servicios_requeridos = [TiempoComida.DESAYUNO, TiempoComida.ALMUERZO, TiempoComida.CENA]
        
        # Obtener ubicaciones activas (de charolas existentes o configuración)
        try:
            ubicaciones = db.query(Charola.ubicacion).distinct().all()
            ubicaciones_list = [u[0] for u in ubicaciones] if ubicaciones else ['principal']
        except Exception:
            ubicaciones_list = ['principal']
        
        for ubicacion in ubicaciones_list:
            for servicio in servicios_requeridos:
                # Verificar si existe programación para este servicio y ubicación que incluya esta fecha
                # Usar el valor del enum (minúsculas) para comparar con PostgreSQL String
                programacion = db.query(ProgramacionMenu).filter(
                    and_(
                        ProgramacionMenu.fecha_desde <= fecha,
                        ProgramacionMenu.fecha_hasta >= fecha,
                        ProgramacionMenu.tiempo_comida == servicio.value,  # Usar valor (minúsculas) para String
                        ProgramacionMenu.ubicacion == ubicacion
                    )
                ).first()
                
                if not programacion:
                    # Verificar si ya existe un ticket para esta falta de programación
                    ticket_existente = db.query(Ticket).filter(
                        and_(
                            Ticket.origen_modulo == 'programacion',
                            Ticket.auto_generado == 'true',
                            func.date(Ticket.fecha_creacion) == fecha,
                            Ticket.descripcion.like(f'%{servicio.value}%{ubicacion}%')
                        )
                    ).first()
                    
                    if ticket_existente:
                        continue
                    
                    asunto = f"Falta programación - {servicio.value.capitalize()} - {ubicacion}"
                    descripcion = (
                        f"No se ha programado el menú para el servicio de {servicio.value} "
                        f"del {fecha.strftime('%d/%m/%Y')} en {ubicacion}.\n\n"
                        f"Sin programación no se puede:\n"
                        f"- Determinar qué menús servir\n"
                        f"- Calcular compras necesarias\n"
                        f"- Verificar stock adecuado\n"
                        f"- Planificar charolas a servir\n\n"
                        f"Fecha: {fecha.strftime('%d/%m/%Y')}\n"
                        f"Servicio: {servicio.value}\n"
                        f"Ubicación: {ubicacion}"
                    )
                    
                    ticket = Ticket(
                        cliente_id=0,  # Tickets automáticos usan cliente dummy id=0
                        tipo=TipoTicket.CONSULTA,
                        asunto=asunto,
                        descripcion=descripcion,
                        estado=EstadoTicket.ABIERTO,
                        prioridad=PrioridadTicket.ALTA,
                        origen_modulo='programacion',
                        auto_generado='true'
                    )
                    
                    db.add(ticket)
                    tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def verificar_reportes_faltantes(db: Session, fecha: date = None) -> List[Ticket]:
        """
        Verifica si faltan reportes de charolas/mermas después del tiempo límite (2 horas).
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha a verificar (por defecto hoy)
            
        Returns:
            Lista de tickets generados
        """
        if fecha is None:
            fecha = date.today()
        
        tickets_generados = []
        ahora = datetime.now()
        
        for servicio_enum, hora_servicio in TicketsAutomaticosService.HORARIOS_SERVICIO.items():
            servicio = servicio_enum.value
            
            # Calcular hora límite (2 horas después del servicio)
            hora_limite = datetime.combine(fecha, hora_servicio) + TicketsAutomaticosService.TIEMPO_LIMITE_REPORTE
            
            # Solo verificar si ya pasó el tiempo límite
            if ahora < hora_limite:
                continue
            
            # Verificar si hay programación para este servicio que incluya esta fecha
            # Usar el valor del enum (minúsculas) para comparar con PostgreSQL String
            programaciones = db.query(ProgramacionMenu).filter(
                and_(
                    ProgramacionMenu.fecha_desde <= fecha,
                    ProgramacionMenu.fecha_hasta >= fecha,
                    ProgramacionMenu.tiempo_comida == servicio_enum.value  # Usar valor (minúsculas) para String
                )
            ).all()
            
            for programacion in programaciones:
                # Verificar si hay charolas reportadas para este servicio
                # Charola.tiempo_comida es String, comparar con valor (minúsculas) del enum
                charolas_reportadas = db.query(Charola).filter(
                    and_(
                        func.date(Charola.fecha_servicio) == fecha,
                        Charola.tiempo_comida == servicio_enum.value,  # Usar valor (minúsculas) para String
                        Charola.ubicacion == programacion.ubicacion
                    )
                ).count()
                
                # Si hay programación pero no hay reporte de charolas
                if programacion.charolas_planificadas > 0 and charolas_reportadas == 0:
                    # Verificar si ya existe un ticket para este reporte faltante
                    ticket_existente = db.query(Ticket).filter(
                        and_(
                            Ticket.programacion_id == programacion.id,
                            Ticket.origen_modulo == 'charola',
                            Ticket.auto_generado == 'true',
                            Ticket.descripcion.like('%reporte faltante%'),
                            func.date(Ticket.fecha_creacion) == fecha
                        )
                    ).first()
                    
                    if ticket_existente:
                        continue
                    
                    asunto = f"Reporte faltante - {servicio.capitalize()} - {programacion.ubicacion}"
                    descripcion = (
                        f"No se ha ingresado el reporte de charolas para el servicio de {servicio} "
                        f"del {fecha.strftime('%d/%m/%Y')} en {programacion.ubicacion}.\n\n"
                        f"Tiempo límite: {hora_limite.strftime('%d/%m/%Y %H:%M')}\n"
                        f"Charolas planificadas: {programacion.charolas_planificadas}\n"
                        f"Charolas reportadas: {charolas_reportadas}\n\n"
                        f"El encargado debe ingresar manualmente el reporte en tiempo.\n"
                        f"Si no lo genera hasta 2 horas después del servicio, se autogenera este ticket.\n\n"
                        f"Programación ID: {programacion.id}"
                    )
                    
                    ticket = Ticket(
                        cliente_id=0,  # Tickets automáticos usan cliente dummy id=0
                        tipo=TipoTicket.CONSULTA,
                        asunto=asunto,
                        descripcion=descripcion,
                        estado=EstadoTicket.ABIERTO,
                        prioridad=PrioridadTicket.MEDIA,
                        programacion_id=programacion.id,
                        origen_modulo='charola',
                        auto_generado='true'
                    )
                    
                    db.add(ticket)
                    tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def verificar_proveedores_items_insuficientes(db: Session, programacion_id: int) -> List[Ticket]:
        """
        Verifica si al programar faltan items y se requiere compra, genera ticket vinculado a proveedor/pedido.
        
        Args:
            db: Sesión de base de datos
            programacion_id: ID de la programación
            
        Returns:
            Lista de tickets generados
        """
        from modules.planificacion.requerimientos import RequerimientosService
        
        tickets_generados = []
        
        programacion = db.query(ProgramacionMenu).filter(
            ProgramacionMenu.id == programacion_id
        ).first()
        
        if not programacion:
            return tickets_generados
        
        # Calcular requerimientos usando fecha_desde
        requerimientos_data = RequerimientosService.calcular_requerimientos_quincenales(
            db, programacion.fecha_desde
        )
        
        # Verificar items con proveedor pero sin stock suficiente
        for req in requerimientos_data['requerimientos']:
            if req['cantidad_a_pedir'] > 0 and req.get('proveedor'):
                # Verificar si ya existe un ticket para este item/proveedor/programación
                ticket_existente = db.query(Ticket).filter(
                    and_(
                        Ticket.programacion_id == programacion_id,
                        Ticket.proveedor_id == req['proveedor'].id,
                        Ticket.origen_modulo == 'proveedor',
                        Ticket.auto_generado == 'true'
                    )
                ).first()
                
                if ticket_existente:
                    continue
                
                # Buscar pedido relacionado si existe
                pedido = db.query(PedidoCompra).filter(
                    and_(
                        PedidoCompra.proveedor_id == req['proveedor'].id,
                        PedidoCompra.estado.in_([EstadoPedido.BORRADOR, EstadoPedido.ENVIADO]),
                        func.date(PedidoCompra.fecha_pedido) >= programacion.fecha_desde,
                        func.date(PedidoCompra.fecha_pedido) <= programacion.fecha_hasta
                    )
                ).first()
                
                asunto = f"Items insuficientes - {req['proveedor'].nombre}"
                fecha_str = programacion.fecha_desde.strftime('%d/%m/%Y')
                if programacion.fecha_desde != programacion.fecha_hasta:
                    fecha_str += f" al {programacion.fecha_hasta.strftime('%d/%m/%Y')}"
                descripcion = (
                    f"Al programar el menú del {fecha_str} "
                    f"se detectó que faltan items que requieren compra.\n\n"
                    f"Item: {req['item'].nombre}\n"
                    f"Cantidad necesaria: {req['cantidad_necesaria']:.2f} {req['unidad']}\n"
                    f"Cantidad actual: {req['cantidad_actual']:.2f} {req['unidad']}\n"
                    f"Cantidad a pedir: {req['cantidad_a_pedir']:.2f} {req['unidad']}\n\n"
                    f"Proveedor: {req['proveedor'].nombre}\n"
                    f"Programación ID: {programacion.id}"
                )
                
                if pedido:
                    descripcion += f"\nPedido relacionado ID: {pedido.id}"
                
                ticket = Ticket(
                    cliente_id=None,  # Tickets automáticos no tienen cliente asociado
                    tipo=TipoTicket.CONSULTA,
                    asunto=asunto,
                    descripcion=descripcion,
                    estado=EstadoTicket.ABIERTO,
                    prioridad=PrioridadTicket.ALTA,
                    programacion_id=programacion_id,
                    proveedor_id=req['proveedor'].id,
                    pedido_id=pedido.id if pedido else None,
                    origen_modulo='proveedor',
                    auto_generado='true'
                )
                
                db.add(ticket)
                tickets_generados.append(ticket)
        
        db.commit()
        return tickets_generados
    
    @staticmethod
    def ejecutar_verificaciones_completas(db: Session, fecha: date = None) -> Dict:
        """
        Ejecuta todas las verificaciones y genera tickets automáticos.
        
        Args:
            db: Sesión de base de datos
            fecha: Fecha a verificar (por defecto hoy)
            
        Returns:
            Diccionario con resumen de tickets generados
        """
        if fecha is None:
            fecha = date.today()
        
        resultado = {
            'fecha': fecha.isoformat(),
            'tickets_generados': {
                'charolas': [],
                'mermas': [],
                'inventario': [],
                'programacion': [],
                'reportes_faltantes': [],
                'proveedores': []
            },
            'total': 0
        }
        
        # Verificar charolas vs planificación
        tickets_charolas = TicketsAutomaticosService.verificar_charolas_vs_planificacion(db, fecha)
        resultado['tickets_generados']['charolas'] = [t.id for t in tickets_charolas]
        
        # Verificar mermas
        tickets_mermas = TicketsAutomaticosService.verificar_mermas_limites(db, fecha)
        resultado['tickets_generados']['mermas'] = [t.id for t in tickets_mermas]
        
        # Verificar inventario
        tickets_inventario = TicketsAutomaticosService.verificar_inventario_seguridad(db)
        resultado['tickets_generados']['inventario'] = [t.id for t in tickets_inventario]
        
        # Verificar programación faltante
        tickets_programacion = TicketsAutomaticosService.verificar_programacion_faltante(db, fecha)
        resultado['tickets_generados']['programacion'] = [t.id for t in tickets_programacion]
        
        # Verificar reportes faltantes
        tickets_reportes = TicketsAutomaticosService.verificar_reportes_faltantes(db, fecha)
        resultado['tickets_generados']['reportes_faltantes'] = [t.id for t in tickets_reportes]
        
        resultado['total'] = (
            len(tickets_charolas) + len(tickets_mermas) + len(tickets_inventario) +
            len(tickets_programacion) + len(tickets_reportes)
        )
        
        return resultado
