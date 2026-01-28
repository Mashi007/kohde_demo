"""
Lógica de negocio para plan contable (centro de cuentas).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models import CuentaContable
from models.contabilidad import TipoCuenta

class CuentaContableService:
    """Servicio para gestión del plan contable."""
    
    @staticmethod
    def crear_cuenta(db: Session, datos: Dict) -> CuentaContable:
        """
        Crea una nueva cuenta contable.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos de la cuenta
            
        Returns:
            Cuenta contable creada
        """
        # Verificar que el código no exista
        existente = db.query(CuentaContable).filter(
            CuentaContable.codigo == datos['codigo']
        ).first()
        
        if existente:
            raise ValueError("Ya existe una cuenta con este código")
        
        cuenta = CuentaContable(**datos)
        db.add(cuenta)
        db.commit()
        db.refresh(cuenta)
        return cuenta
    
    @staticmethod
    def obtener_cuenta(db: Session, cuenta_id: int) -> Optional[CuentaContable]:
        """Obtiene una cuenta por ID."""
        return db.query(CuentaContable).filter(CuentaContable.id == cuenta_id).first()
    
    @staticmethod
    def listar_cuentas(
        db: Session,
        tipo: Optional[str] = None,
        padre_id: Optional[int] = None
    ) -> List[CuentaContable]:
        """
        Lista cuentas contables con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            tipo: Filtrar por tipo de cuenta
            padre_id: Filtrar por cuenta padre
            
        Returns:
            Lista de cuentas
        """
        query = db.query(CuentaContable)
        
        if tipo:
            query = query.filter(CuentaContable.tipo == TipoCuenta[tipo.upper()])
        
        if padre_id:
            query = query.filter(CuentaContable.padre_id == padre_id)
        else:
            # Por defecto, solo cuentas principales (sin padre)
            query = query.filter(CuentaContable.padre_id.is_(None))
        
        return query.order_by(CuentaContable.codigo).all()
    
    @staticmethod
    def obtener_arbol_cuentas(db: Session) -> List[Dict]:
        """
        Obtiene el árbol completo de cuentas contables.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de cuentas con estructura jerárquica
        """
        cuentas = db.query(CuentaContable).order_by(CuentaContable.codigo).all()
        
        # Construir árbol
        cuenta_dict = {c.id: c.to_dict() for c in cuentas}
        arbol = []
        
        for cuenta in cuentas:
            cuenta_data = cuenta_dict[cuenta.id]
            if cuenta.padre_id:
                if 'hijos' not in cuenta_dict[cuenta.padre_id]:
                    cuenta_dict[cuenta.padre_id]['hijos'] = []
                cuenta_dict[cuenta.padre_id]['hijos'].append(cuenta_data)
            else:
                arbol.append(cuenta_data)
        
        return arbol
