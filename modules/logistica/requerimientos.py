"""
Lógica de negocio para requerimientos (salidas de bodega).
"""
from typing import List, Optional, Dict
from datetime import datetime, time
from sqlalchemy.orm import Session
from models import Requerimiento, RequerimientoItem, Inventario
from models.requerimiento import EstadoRequerimiento
from modules.logistica.inventario import InventarioService

class RequerimientoService:
    """Servicio para gestión de requerimientos."""
    
    @staticmethod
    def crear_requerimiento(db: Session, datos: Dict) -> Requerimiento:
        """
        Crea un nuevo requerimiento.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del requerimiento
            
        Returns:
            Requerimiento creado
        """
        requerimiento = Requerimiento(
            solicitante=datos['solicitante'],
            receptor=datos['receptor'],
            observaciones=datos.get('observaciones')
        )
        
        db.add(requerimiento)
        db.flush()  # Para obtener el ID
        
        # Crear items del requerimiento
        for item_data in datos.get('items', []):
            item_id = item_data['item_id']
            cantidad = float(item_data['cantidad_solicitada'])
            
            # Verificar disponibilidad
            disponibilidad = InventarioService.verificar_disponibilidad(db, item_id, cantidad)
            
            if not disponibilidad['suficiente']:
                raise ValueError(
                    f"Stock insuficiente para {item_data.get('nombre', 'item')}. "
                    f"Disponible: {disponibilidad['cantidad_disponible']}, "
                    f"Necesario: {cantidad}"
                )
            
            requerimiento_item = RequerimientoItem(
                requerimiento_id=requerimiento.id,
                item_id=item_id,
                cantidad_solicitada=cantidad
            )
            db.add(requerimiento_item)
        
        db.commit()
        db.refresh(requerimiento)
        return requerimiento
    
    @staticmethod
    def procesar_requerimiento(db: Session, requerimiento_id: int) -> Requerimiento:
        """
        Procesa un requerimiento entregando los items y actualizando inventario.
        
        Args:
            db: Sesión de base de datos
            requerimiento_id: ID del requerimiento
            
        Returns:
            Requerimiento procesado
        """
        requerimiento = db.query(Requerimiento).filter(
            Requerimiento.id == requerimiento_id
        ).first()
        
        if not requerimiento:
            raise ValueError("Requerimiento no encontrado")
        
        if requerimiento.estado == EstadoRequerimiento.ENTREGADO:
            raise ValueError("El requerimiento ya fue entregado")
        
        # Procesar cada item
        for item_req in requerimiento.items:
            cantidad_entregada = float(item_req.cantidad_solicitada)
            
            # Actualizar inventario (salida)
            InventarioService.actualizar_stock(
                db,
                item_req.item_id,
                cantidad_entregada,
                operacion='salida'
            )
            
            # Registrar cantidad entregada y hora
            item_req.cantidad_entregada = cantidad_entregada
            item_req.hora_entrega = datetime.utcnow().time()
        
        # Marcar como entregado
        requerimiento.estado = EstadoRequerimiento.ENTREGADO
        
        db.commit()
        db.refresh(requerimiento)
        return requerimiento
    
    @staticmethod
    def listar_requerimientos(
        db: Session,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requerimiento]:
        """
        Lista requerimientos con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            estado: Filtrar por estado
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de requerimientos
        """
        query = db.query(Requerimiento)
        
        if estado:
            query = query.filter(Requerimiento.estado == EstadoRequerimiento[estado.upper()])
        
        return query.order_by(Requerimiento.fecha.desc()).offset(skip).limit(limit).all()
