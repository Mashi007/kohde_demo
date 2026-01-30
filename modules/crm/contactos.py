"""
Servicio para gestión de contactos (CRM).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from models.contacto import Contacto, TipoContacto
from models import Proveedor

class ContactoService:
    """Servicio para gestión de contactos."""
    
    @staticmethod
    def listar_contactos(
        db: Session,
        tipo: Optional[str] = None,
        proveedor_id: Optional[int] = None,
        proyecto: Optional[str] = None,
        activo: Optional[bool] = True,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Contacto]:
        """
        Lista contactos con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            tipo: Filtrar por tipo (proveedor/colaborador)
            proveedor_id: Filtrar por proveedor
            proyecto: Filtrar por proyecto
            activo: Filtrar por estado activo
            busqueda: Búsqueda en nombre, email, proyecto, cargo
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de contactos
        """
        query = db.query(Contacto)
        
        # Filtros
        if tipo:
            try:
                tipo_enum = TipoContacto[tipo.upper()]
                query = query.filter(Contacto.tipo == tipo_enum)
            except (KeyError, AttributeError):
                pass
        
        if proveedor_id is not None:
            query = query.filter(Contacto.proveedor_id == proveedor_id)
        
        if proyecto:
            query = query.filter(Contacto.proyecto.ilike(f'%{proyecto}%'))
        
        if activo is not None:
            query = query.filter(Contacto.activo == activo)
        
        if busqueda:
            busqueda_filter = or_(
                Contacto.nombre.ilike(f'%{busqueda}%'),
                Contacto.email.ilike(f'%{busqueda}%'),
                Contacto.proyecto.ilike(f'%{busqueda}%'),
                Contacto.cargo.ilike(f'%{busqueda}%')
            )
            query = query.filter(busqueda_filter)
        
        return query.order_by(Contacto.nombre.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_contacto(db: Session, contacto_id: int) -> Optional[Contacto]:
        """Obtiene un contacto por ID."""
        return db.query(Contacto).filter(Contacto.id == contacto_id).first()
    
    @staticmethod
    def crear_contacto(
        db: Session,
        nombre: str,
        email: Optional[str] = None,
        whatsapp: Optional[str] = None,
        telefono: Optional[str] = None,
        proyecto: Optional[str] = None,
        cargo: Optional[str] = None,
        tipo: str = 'proveedor',
        proveedor_id: Optional[int] = None,
        notas: Optional[str] = None
    ) -> Contacto:
        """
        Crea un nuevo contacto.
        
        Args:
            db: Sesión de base de datos
            nombre: Nombre del contacto
            email: Email del contacto
            whatsapp: Número de WhatsApp
            telefono: Teléfono
            proyecto: Proyecto asociado
            cargo: Cargo/posición
            tipo: Tipo de contacto (proveedor/colaborador)
            proveedor_id: ID del proveedor (si es tipo proveedor)
            notas: Notas adicionales
            
        Returns:
            Contacto creado
        """
        # Validar tipo
        try:
            tipo_enum = TipoContacto[tipo.upper()]
        except (KeyError, AttributeError):
            tipo_enum = TipoContacto.PROVEEDOR
        
        # Validar proveedor si se proporciona
        if proveedor_id:
            proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
            if not proveedor:
                raise ValueError(f"Proveedor con ID {proveedor_id} no encontrado")
        
        contacto = Contacto(
            nombre=nombre,
            email=email,
            whatsapp=whatsapp,
            telefono=telefono,
            proyecto=proyecto,
            cargo=cargo,
            tipo=tipo_enum,
            proveedor_id=proveedor_id,
            notas=notas
        )
        
        db.add(contacto)
        db.commit()
        db.refresh(contacto)
        return contacto
    
    @staticmethod
    def actualizar_contacto(
        db: Session,
        contacto_id: int,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        whatsapp: Optional[str] = None,
        telefono: Optional[str] = None,
        proyecto: Optional[str] = None,
        cargo: Optional[str] = None,
        tipo: Optional[str] = None,
        proveedor_id: Optional[int] = None,
        notas: Optional[str] = None,
        activo: Optional[bool] = None
    ) -> Contacto:
        """
        Actualiza un contacto existente.
        
        Args:
            db: Sesión de base de datos
            contacto_id: ID del contacto
            **kwargs: Campos a actualizar
            
        Returns:
            Contacto actualizado
        """
        contacto = ContactoService.obtener_contacto(db, contacto_id)
        if not contacto:
            raise ValueError(f"Contacto con ID {contacto_id} no encontrado")
        
        if nombre is not None:
            contacto.nombre = nombre
        if email is not None:
            contacto.email = email
        if whatsapp is not None:
            contacto.whatsapp = whatsapp
        if telefono is not None:
            contacto.telefono = telefono
        if proyecto is not None:
            contacto.proyecto = proyecto
        if cargo is not None:
            contacto.cargo = cargo
        if tipo is not None:
            try:
                contacto.tipo = TipoContacto[tipo.upper()]
            except (KeyError, AttributeError):
                pass
        if proveedor_id is not None:
            if proveedor_id:
                proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
                if not proveedor:
                    raise ValueError(f"Proveedor con ID {proveedor_id} no encontrado")
            contacto.proveedor_id = proveedor_id
        if notas is not None:
            contacto.notas = notas
        if activo is not None:
            contacto.activo = activo
        
        contacto.fecha_actualizacion = datetime.utcnow()
        db.commit()
        db.refresh(contacto)
        return contacto
    
    @staticmethod
    def eliminar_contacto(db: Session, contacto_id: int) -> bool:
        """
        Elimina un contacto (marca como inactivo).
        
        Args:
            db: Sesión de base de datos
            contacto_id: ID del contacto
            
        Returns:
            True si se eliminó correctamente
        """
        contacto = ContactoService.obtener_contacto(db, contacto_id)
        if not contacto:
            return False
        
        contacto.activo = False
        contacto.fecha_actualizacion = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def enviar_mensaje_email(
        db: Session,
        contacto_id: int,
        asunto: str,
        contenido: str
    ) -> Dict:
        """
        Envía un mensaje por email a un contacto.
        
        Args:
            db: Sesión de base de datos
            contacto_id: ID del contacto
            asunto: Asunto del email
            contenido: Contenido del email
            
        Returns:
            Resultado del envío
        """
        contacto = ContactoService.obtener_contacto(db, contacto_id)
        if not contacto:
            raise ValueError(f"Contacto con ID {contacto_id} no encontrado")
        
        if not contacto.email:
            raise ValueError("El contacto no tiene email configurado")
        
        try:
            from modules.crm.notificaciones.email import email_service
            
            contenido_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #7C3AED;">{asunto}</h2>
                    <p>{contenido.replace(chr(10), '<br>')}</p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        Este mensaje fue enviado desde el sistema ERP de restaurantes.
                    </p>
                </div>
            </body>
            </html>
            """
            
            resultado = email_service.enviar_email(
                contacto.email,
                asunto,
                contenido_html
            )
            
            return {
                'exito': True,
                'mensaje': 'Email enviado correctamente',
                'contacto': contacto.nombre,
                'email': contacto.email,
                'resultado': resultado
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar email a contacto {contacto_id}: {e}", exc_info=True)
            return {
                'exito': False,
                'mensaje': f'Error al enviar email: {str(e)}',
                'contacto': contacto.nombre,
                'email': contacto.email
            }
    
    @staticmethod
    def enviar_mensaje_whatsapp(
        db: Session,
        contacto_id: int,
        mensaje: str
    ) -> Dict:
        """
        Envía un mensaje por WhatsApp a un contacto.
        
        Args:
            db: Sesión de base de datos
            contacto_id: ID del contacto
            mensaje: Mensaje a enviar
            
        Returns:
            Resultado del envío
        """
        contacto = ContactoService.obtener_contacto(db, contacto_id)
        if not contacto:
            raise ValueError(f"Contacto con ID {contacto_id} no encontrado")
        
        if not contacto.whatsapp:
            raise ValueError("El contacto no tiene WhatsApp configurado")
        
        try:
            from modules.crm.notificaciones.whatsapp import whatsapp_service
            
            # Limpiar número de WhatsApp (solo dígitos)
            import re
            numero_limpio = re.sub(r'[^0-9]', '', contacto.whatsapp)
            
            resultado = whatsapp_service.enviar_mensaje(
                numero_limpio,
                mensaje
            )
            
            return {
                'exito': True,
                'mensaje': 'Mensaje de WhatsApp enviado correctamente',
                'contacto': contacto.nombre,
                'whatsapp': contacto.whatsapp,
                'resultado': resultado
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al enviar WhatsApp a contacto {contacto_id}: {e}", exc_info=True)
            return {
                'exito': False,
                'mensaje': f'Error al enviar WhatsApp: {str(e)}',
                'contacto': contacto.nombre,
                'whatsapp': contacto.whatsapp
            }

# Instancia global del servicio
contacto_service = ContactoService()
