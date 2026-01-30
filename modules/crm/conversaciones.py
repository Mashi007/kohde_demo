"""
Servicio para gestión de conversaciones con contactos (CRM).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

from models.conversacion_contacto import ConversacionContacto, TipoMensajeContacto, DireccionMensaje
from models.contacto import Contacto

class ConversacionService:
    """Servicio para gestión de conversaciones con contactos."""
    
    @staticmethod
    def listar_conversaciones(
        db: Session,
        contacto_id: Optional[int] = None,
        tipo_mensaje: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConversacionContacto]:
        """
        Lista conversaciones con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            contacto_id: Filtrar por contacto
            tipo_mensaje: Filtrar por tipo (email/whatsapp)
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de conversaciones ordenadas por fecha descendente
        """
        query = db.query(ConversacionContacto)
        
        if contacto_id:
            query = query.filter(ConversacionContacto.contacto_id == contacto_id)
        
        if tipo_mensaje:
            try:
                tipo_enum = TipoMensajeContacto[tipo_mensaje.upper()]
                query = query.filter(ConversacionContacto.tipo_mensaje == tipo_enum)
            except (KeyError, AttributeError):
                pass
        
        return query.order_by(desc(ConversacionContacto.fecha_envio)).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_conversacion(db: Session, conversacion_id: int) -> Optional[ConversacionContacto]:
        """Obtiene una conversación por ID."""
        return db.query(ConversacionContacto).filter(ConversacionContacto.id == conversacion_id).first()
    
    @staticmethod
    def crear_conversacion(
        db: Session,
        contacto_id: int,
        tipo_mensaje: str,
        contenido: str,
        asunto: Optional[str] = None,
        mensaje_id_externo: Optional[str] = None,
        estado: str = 'enviado',
        error: Optional[str] = None
    ) -> ConversacionContacto:
        """
        Crea un nuevo registro de conversación.
        
        Args:
            db: Sesión de base de datos
            contacto_id: ID del contacto
            tipo_mensaje: Tipo de mensaje ('email' o 'whatsapp')
            contenido: Contenido del mensaje
            asunto: Asunto (solo para emails)
            mensaje_id_externo: ID del mensaje en el servicio externo
            estado: Estado del mensaje
            error: Mensaje de error si falló
            
        Returns:
            Conversación creada
        """
        # Validar contacto
        contacto = db.query(Contacto).filter(Contacto.id == contacto_id).first()
        if not contacto:
            raise ValueError(f"Contacto con ID {contacto_id} no encontrado")
        
        # Validar tipo
        try:
            tipo_enum = TipoMensajeContacto[tipo_mensaje.upper()]
        except (KeyError, AttributeError):
            raise ValueError(f"Tipo de mensaje inválido: {tipo_mensaje}. Debe ser 'email' o 'whatsapp'")
        
        # Validar que el contacto tenga el canal configurado
        if tipo_enum == TipoMensajeContacto.EMAIL and not contacto.email:
            raise ValueError("El contacto no tiene email configurado")
        if tipo_enum == TipoMensajeContacto.WHATSAPP and not contacto.whatsapp:
            raise ValueError("El contacto no tiene WhatsApp configurado")
        
        conversacion = ConversacionContacto(
            contacto_id=contacto_id,
            tipo_mensaje=tipo_enum,
            direccion=DireccionMensaje.ENVIADO,
            asunto=asunto,
            contenido=contenido,
            mensaje_id_externo=mensaje_id_externo,
            estado=estado,
            error=error
        )
        
        db.add(conversacion)
        db.commit()
        db.refresh(conversacion)
        return conversacion
    
    @staticmethod
    def obtener_ultimas_conversaciones_por_contacto(
        db: Session,
        limite_por_contacto: int = 5
    ) -> Dict[int, List[ConversacionContacto]]:
        """
        Obtiene las últimas conversaciones agrupadas por contacto.
        Útil para mostrar vista de CRM con últimos mensajes.
        
        Args:
            db: Sesión de base de datos
            limite_por_contacto: Número de conversaciones por contacto
            
        Returns:
            Diccionario con contacto_id como clave y lista de conversaciones como valor
        """
        # Obtener todos los contactos activos
        contactos = db.query(Contacto).filter(Contacto.activo == True).all()
        
        resultado = {}
        for contacto in contactos:
            conversaciones = db.query(ConversacionContacto).filter(
                ConversacionContacto.contacto_id == contacto.id
            ).order_by(desc(ConversacionContacto.fecha_envio)).limit(limite_por_contacto).all()
            
            if conversaciones:
                resultado[contacto.id] = conversaciones
        
        return resultado
    
    @staticmethod
    def obtener_resumen_conversaciones(db: Session) -> Dict:
        """
        Obtiene un resumen de conversaciones para estadísticas.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Diccionario con estadísticas
        """
        total = db.query(ConversacionContacto).count()
        total_email = db.query(ConversacionContacto).filter(
            ConversacionContacto.tipo_mensaje == TipoMensajeContacto.EMAIL
        ).count()
        total_whatsapp = db.query(ConversacionContacto).filter(
            ConversacionContacto.tipo_mensaje == TipoMensajeContacto.WHATSAPP
        ).count()
        total_exitosas = db.query(ConversacionContacto).filter(
            ConversacionContacto.estado.in_(['enviado', 'entregado', 'leido'])
        ).count()
        total_fallidas = db.query(ConversacionContacto).filter(
            ConversacionContacto.estado == 'error'
        ).count()
        
        return {
            'total': total,
            'total_email': total_email,
            'total_whatsapp': total_whatsapp,
            'total_exitosas': total_exitosas,
            'total_fallidas': total_fallidas
        }

# Instancia global del servicio
conversacion_service = ConversacionService()
