"""
Lógica de negocio para gestión de proveedores.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models import Proveedor, Factura, PedidoCompra
from utils.validators import validate_email, validate_phone, validate_ruc

class ProveedorService:
    """Servicio para gestión de proveedores."""
    
    @staticmethod
    def crear_proveedor(db: Session, datos: Dict) -> Proveedor:
        """
        Crea un nuevo proveedor.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del proveedor
            
        Returns:
            Proveedor creado
        """
        # Validaciones
        if datos.get('email') and not validate_email(datos['email']):
            raise ValueError("Email inválido")
        
        if datos.get('telefono') and not validate_phone(datos['telefono']):
            raise ValueError("Teléfono inválido")
        
        if datos.get('ruc') and not validate_ruc(datos['ruc']):
            raise ValueError("RUC inválido")
        
        # Verificar duplicados
        if datos.get('ruc'):
            existente = db.query(Proveedor).filter(Proveedor.ruc == datos['ruc']).first()
            if existente:
                raise ValueError("Ya existe un proveedor con este RUC")
        
        proveedor = Proveedor(**datos)
        db.add(proveedor)
        db.commit()
        db.refresh(proveedor)
        return proveedor
    
    @staticmethod
    def obtener_proveedor(db: Session, proveedor_id: int) -> Optional[Proveedor]:
        """Obtiene un proveedor por ID."""
        return db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    
    @staticmethod
    def listar_proveedores(
        db: Session,
        activo: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Proveedor]:
        """
        Lista proveedores con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            activo: Filtrar por estado activo
            busqueda: Búsqueda por nombre o RUC
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de proveedores
        """
        from sqlalchemy import or_
        
        query = db.query(Proveedor)
        
        if activo is not None:
            query = query.filter(Proveedor.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Proveedor.nombre.ilike(f'%{busqueda}%'),
                    Proveedor.ruc.ilike(f'%{busqueda}%')
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_historial_facturas(db: Session, proveedor_id: int) -> List[Factura]:
        """Obtiene el historial de facturas de un proveedor."""
        return db.query(Factura).filter(
            Factura.proveedor_id == proveedor_id,
            Factura.tipo == 'proveedor'
        ).order_by(Factura.fecha_emision.desc()).all()
    
    @staticmethod
    def obtener_historial_pedidos(db: Session, proveedor_id: int) -> List[PedidoCompra]:
        """Obtiene el historial de pedidos de un proveedor."""
        return db.query(PedidoCompra).filter(
            PedidoCompra.proveedor_id == proveedor_id
        ).order_by(PedidoCompra.fecha_pedido.desc()).all()
