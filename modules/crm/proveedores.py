"""
Lógica de negocio para gestión de proveedores.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models import Proveedor, Factura, PedidoCompra, Item, ItemLabel
from models.item_label import item_labels
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
        label_id: Optional[int] = None,  # Filtrar por label/clasificación
        skip: int = 0,
        limit: int = 100
    ) -> List[Proveedor]:
        """
        Lista proveedores con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            activo: Filtrar por estado activo
            busqueda: Búsqueda por nombre o RUC
            label_id: Filtrar por label/clasificación de items que provee
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de proveedores
        """
        query = db.query(Proveedor).distinct()
        
        if activo is not None:
            query = query.filter(Proveedor.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Proveedor.nombre.ilike(f'%{busqueda}%'),
                    Proveedor.ruc.ilike(f'%{busqueda}%')
                )
            )
        
        # Filtrar por label: proveedores que tienen items con esta clasificación
        if label_id:
            query = query.join(Item, Item.proveedor_autorizado_id == Proveedor.id)\
                         .join(item_labels, item_labels.c.item_id == Item.id)\
                         .filter(item_labels.c.label_id == label_id)\
                         .filter(Item.activo == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_proveedor_con_items_labels(db: Session, proveedor_id: int) -> Optional[Dict]:
        """
        Obtiene un proveedor con sus items y labels agrupados.
        
        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor
            
        Returns:
            Diccionario con proveedor y sus items/labels
        """
        proveedor = ProveedorService.obtener_proveedor(db, proveedor_id)
        if not proveedor:
            return None
        
        # Obtener items del proveedor con sus labels
        items = db.query(Item).filter(
            Item.proveedor_autorizado_id == proveedor_id,
            Item.activo == True
        ).all()
        
        # Agrupar labels por categoría
        labels_por_categoria = {}
        labels_todos = set()
        
        for item in items:
            for label in item.labels:
                if label.activo:
                    cat = label.categoria_principal
                    if cat not in labels_por_categoria:
                        labels_por_categoria[cat] = []
                    if label.id not in [l['id'] for l in labels_por_categoria[cat]]:
                        labels_por_categoria[cat].append({
                            'id': label.id,
                            'codigo': label.codigo,
                            'nombre_es': label.nombre_es,
                            'nombre_en': label.nombre_en
                        })
                    labels_todos.add(label.id)
        
        return {
            'proveedor': proveedor.to_dict(),
            'items': [item.to_dict() for item in items],
            'labels_por_categoria': labels_por_categoria,
            'total_items': len(items),
            'total_labels': len(labels_todos)
        }
    
    @staticmethod
    def actualizar_proveedor(db: Session, proveedor_id: int, datos: Dict) -> Proveedor:
        """
        Actualiza un proveedor existente.
        
        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor
            datos: Datos a actualizar
            
        Returns:
            Proveedor actualizado
        """
        proveedor = ProveedorService.obtener_proveedor(db, proveedor_id)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")
        
        # Validaciones si se actualizan estos campos
        if 'email' in datos and datos['email'] and not validate_email(datos['email']):
            raise ValueError("Email inválido")
        
        if 'telefono' in datos and datos['telefono'] and not validate_phone(datos['telefono']):
            raise ValueError("Teléfono inválido")
        
        if 'ruc' in datos and datos['ruc']:
            if not validate_ruc(datos['ruc']):
                raise ValueError("RUC inválido")
            # Verificar duplicados si cambió el RUC
            if datos['ruc'] != proveedor.ruc:
                existente = db.query(Proveedor).filter(Proveedor.ruc == datos['ruc']).first()
                if existente:
                    raise ValueError("Ya existe un proveedor con este RUC")
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(proveedor, key) and key != 'id':
                setattr(proveedor, key, value)
        
        db.commit()
        db.refresh(proveedor)
        return proveedor
    
    @staticmethod
    def eliminar_proveedor(db: Session, proveedor_id: int) -> bool:
        """
        Elimina (soft delete) un proveedor.
        
        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor
            
        Returns:
            True si se eliminó correctamente
        """
        proveedor = ProveedorService.obtener_proveedor(db, proveedor_id)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")
        
        # Soft delete: marcar como inactivo
        proveedor.activo = False
        db.commit()
        return True
    
    @staticmethod
    def toggle_activo(db: Session, proveedor_id: int) -> Proveedor:
        """
        Alterna el estado activo/inactivo de un proveedor.
        
        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor
            
        Returns:
            Proveedor actualizado
        """
        proveedor = ProveedorService.obtener_proveedor(db, proveedor_id)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")
        
        proveedor.activo = not proveedor.activo
        db.commit()
        db.refresh(proveedor)
        return proveedor
    
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
