"""
Lógica de negocio para gestión de tickets.
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Ticket
from models.ticket import EstadoTicket, TipoTicket, PrioridadTicket

class TicketService:
    """Servicio para gestión de tickets."""
    
    @staticmethod
    def crear_ticket(db: Session, datos: Dict) -> Ticket:
        """
        Crea un nuevo ticket.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del ticket
            
        Returns:
            Ticket creado
        """
        # cliente_id es ahora opcional (módulo Cliente eliminado)
        # Si se proporciona, se guarda pero no se valida
        
        # Convertir strings a enums si es necesario
        ticket_data = datos.copy()
        if isinstance(ticket_data.get('tipo'), str):
            ticket_data['tipo'] = TipoTicket[ticket_data['tipo'].upper()]
        if isinstance(ticket_data.get('prioridad'), str):
            ticket_data['prioridad'] = PrioridadTicket[ticket_data['prioridad'].upper()]
        if isinstance(ticket_data.get('estado'), str):
            ticket_data['estado'] = EstadoTicket[ticket_data['estado'].upper()]
        
        ticket = Ticket(**ticket_data)
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def obtener_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
        """
        Obtiene un ticket por ID.
        
        Args:
            db: Sesión de base de datos
            ticket_id: ID del ticket
            
        Returns:
            Ticket o None si no existe
        """
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    def listar_tickets(
        db: Session,
        cliente_id: Optional[int] = None,
        estado: Optional[str] = None,
        tipo: Optional[str] = None,
        asignado_a: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Ticket]:
        """
        Lista tickets con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            cliente_id: Filtrar por cliente
            estado: Filtrar por estado
            tipo: Filtrar por tipo
            asignado_a: Filtrar por usuario asignado
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de tickets
        """
        query = db.query(Ticket)
        
        if cliente_id:
            query = query.filter(Ticket.cliente_id == cliente_id)
        
        if estado:
            try:
                estado_enum = EstadoTicket[estado.upper()]
                query = query.filter(Ticket.estado == estado_enum)
            except KeyError:
                # Estado inválido, ignorar filtro o retornar error
                # Por ahora ignoramos el filtro si el estado no es válido
                pass
        
        if tipo:
            query = query.filter(Ticket.tipo == TipoTicket[tipo.upper()])
        
        if asignado_a:
            query = query.filter(Ticket.asignado_a == asignado_a)
        
        return query.order_by(Ticket.fecha_creacion.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_ticket(db: Session, ticket_id: int, datos: Dict) -> Ticket:
        """
        Actualiza un ticket existente.
        
        Args:
            db: Sesión de base de datos
            ticket_id: ID del ticket
            datos: Datos a actualizar
            
        Returns:
            Ticket actualizado
        """
        ticket = TicketService.obtener_ticket(db, ticket_id)
        if not ticket:
            raise ValueError("Ticket no encontrado")
        
        # Si se marca como resuelto, actualizar fecha de resolución
        if 'estado' in datos:
            nuevo_estado = EstadoTicket[datos['estado'].upper()] if isinstance(datos['estado'], str) else datos['estado']
            if nuevo_estado == EstadoTicket.RESUELTO and ticket.estado != EstadoTicket.RESUELTO:
                datos['fecha_resolucion'] = datetime.utcnow()
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(ticket, key):
                if key in ['estado', 'tipo', 'prioridad']:
                    # Convertir string a Enum si es necesario
                    enum_class = {
                        'estado': EstadoTicket,
                        'tipo': TipoTicket,
                        'prioridad': PrioridadTicket
                    }[key]
                    if isinstance(value, str):
                        value = enum_class[value.upper()]
                setattr(ticket, key, value)
        
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def asignar_ticket(db: Session, ticket_id: int, usuario_id: int) -> Ticket:
        """
        Asigna un ticket a un usuario.
        
        Args:
            db: Sesión de base de datos
            ticket_id: ID del ticket
            usuario_id: ID del usuario
            
        Returns:
            Ticket actualizado
        """
        ticket = TicketService.obtener_ticket(db, ticket_id)
        if not ticket:
            raise ValueError("Ticket no encontrado")
        
        ticket.asignado_a = usuario_id
        if ticket.estado == EstadoTicket.ABIERTO:
            ticket.estado = EstadoTicket.EN_PROCESO
        
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def resolver_ticket(db: Session, ticket_id: int, respuesta: str) -> Ticket:
        """
        Resuelve un ticket con una respuesta.
        
        Args:
            db: Sesión de base de datos
            ticket_id: ID del ticket
            respuesta: Respuesta al ticket
            
        Returns:
            Ticket resuelto
        """
        ticket = TicketService.obtener_ticket(db, ticket_id)
        if not ticket:
            raise ValueError("Ticket no encontrado")
        
        ticket.estado = EstadoTicket.RESUELTO
        ticket.respuesta = respuesta
        ticket.fecha_resolucion = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        return ticket
