"""
Lógica de negocio para gestión de clientes.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Cliente, Factura, Ticket
from utils.validators import validate_email, validate_phone, validate_ruc

class ClienteService:
    """Servicio para gestión de clientes."""
    
    @staticmethod
    def crear_cliente(db: Session, datos: Dict) -> Cliente:
        """
        Crea un nuevo cliente.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del cliente
            
        Returns:
            Cliente creado
        """
        # Validaciones
        if datos.get('email') and not validate_email(datos['email']):
            raise ValueError("Email inválido")
        
        if datos.get('telefono') and not validate_phone(datos['telefono']):
            raise ValueError("Teléfono inválido")
        
        if datos.get('ruc_ci') and datos.get('tipo') == 'empresa':
            if not validate_ruc(datos['ruc_ci']):
                raise ValueError("RUC inválido")
        
        # Verificar duplicados
        if datos.get('ruc_ci'):
            existente = db.query(Cliente).filter(Cliente.ruc_ci == datos['ruc_ci']).first()
            if existente:
                raise ValueError("Ya existe un cliente con este RUC/CI")
        
        cliente = Cliente(**datos)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente
    
    @staticmethod
    def obtener_cliente(db: Session, cliente_id: int) -> Optional[Cliente]:
        """
        Obtiene un cliente por ID.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            Cliente o None si no existe
        """
        return db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    @staticmethod
    def listar_clientes(
        db: Session,
        activo: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cliente]:
        """
        Lista clientes con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            activo: Filtrar por estado activo
            busqueda: Búsqueda por nombre, RUC o teléfono
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de clientes
        """
        query = db.query(Cliente)
        
        if activo is not None:
            query = query.filter(Cliente.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Cliente.nombre.ilike(f'%{busqueda}%'),
                    Cliente.ruc_ci.ilike(f'%{busqueda}%'),
                    Cliente.telefono.ilike(f'%{busqueda}%')
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_cliente(db: Session, cliente_id: int, datos: Dict) -> Cliente:
        """
        Actualiza un cliente existente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            datos: Datos a actualizar
            
        Returns:
            Cliente actualizado
        """
        cliente = ClienteService.obtener_cliente(db, cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Validaciones
        if 'email' in datos and datos['email'] and not validate_email(datos['email']):
            raise ValueError("Email inválido")
        
        if 'telefono' in datos and datos['telefono'] and not validate_phone(datos['telefono']):
            raise ValueError("Teléfono inválido")
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
        
        db.commit()
        db.refresh(cliente)
        return cliente
    
    @staticmethod
    def eliminar_cliente(db: Session, cliente_id: int) -> bool:
        """
        Elimina (desactiva) un cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            True si se eliminó correctamente
        """
        cliente = ClienteService.obtener_cliente(db, cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        cliente.activo = False
        db.commit()
        return True
    
    @staticmethod
    def obtener_historial_facturas(db: Session, cliente_id: int) -> List[Factura]:
        """
        Obtiene el historial de facturas de un cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            Lista de facturas
        """
        return db.query(Factura).filter(
            Factura.cliente_id == cliente_id,
            Factura.tipo == 'cliente'
        ).order_by(Factura.fecha_emision.desc()).all()
    
    @staticmethod
    def obtener_historial_tickets(db: Session, cliente_id: int) -> List[Ticket]:
        """
        Obtiene el historial de tickets de un cliente.
        
        Args:
            db: Sesión de base de datos
            cliente_id: ID del cliente
            
        Returns:
            Lista de tickets
        """
        return db.query(Ticket).filter(
            Ticket.cliente_id == cliente_id
        ).order_by(Ticket.fecha_creacion.desc()).all()
