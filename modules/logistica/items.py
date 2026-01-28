"""
Lógica de negocio para gestión de items (catálogo de productos).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Item, Inventario
from utils.validators import validate_positive_number

class ItemService:
    """Servicio para gestión de items."""
    
    @staticmethod
    def crear_item(db: Session, datos: Dict) -> Item:
        """
        Crea un nuevo item.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del item
            
        Returns:
            Item creado
        """
        # Validar código único
        if datos.get('codigo'):
            existente = db.query(Item).filter(Item.codigo == datos['codigo']).first()
            if existente:
                raise ValueError("Ya existe un item con este código")
        
        item = Item(**datos)
        db.add(item)
        db.commit()
        db.refresh(item)
        
        # Crear registro de inventario inicial si se especifica cantidad inicial
        if 'cantidad_inicial' in datos:
            inventario = Inventario(
                item_id=item.id,
                cantidad_actual=float(datos['cantidad_inicial']),
                unidad=item.unidad,
                cantidad_minima=float(datos.get('cantidad_minima', 0))
            )
            db.add(inventario)
            db.commit()
        
        return item
    
    @staticmethod
    def obtener_item(db: Session, item_id: int) -> Optional[Item]:
        """Obtiene un item por ID."""
        return db.query(Item).filter(Item.id == item_id).first()
    
    @staticmethod
    def listar_items(
        db: Session,
        categoria: Optional[str] = None,
        activo: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        """
        Lista items con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            categoria: Filtrar por categoría
            activo: Filtrar por estado activo
            busqueda: Búsqueda por nombre o código
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de items
        """
        query = db.query(Item)
        
        if categoria:
            from models.item import CategoriaItem
            query = query.filter(Item.categoria == CategoriaItem[categoria.upper()])
        
        if activo is not None:
            query = query.filter(Item.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Item.nombre.ilike(f'%{busqueda}%'),
                    Item.codigo.ilike(f'%{busqueda}%')
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_item(db: Session, item_id: int, datos: Dict) -> Item:
        """
        Actualiza un item existente.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            datos: Datos a actualizar
            
        Returns:
            Item actualizado
        """
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        # Validar código único si se cambia
        if 'codigo' in datos and datos['codigo'] != item.codigo:
            existente = db.query(Item).filter(Item.codigo == datos['codigo']).first()
            if existente:
                raise ValueError("Ya existe un item con este código")
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(item, key) and key != 'id':
                if key in ['categoria']:
                    from models.item import CategoriaItem
                    if isinstance(value, str):
                        value = CategoriaItem[value.upper()]
                setattr(item, key, value)
        
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def actualizar_costo_unitario(db: Session, item_id: int, costo: float) -> Item:
        """
        Actualiza el costo unitario de un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            costo: Nuevo costo unitario
            
        Returns:
            Item actualizado
        """
        if not validate_positive_number(costo):
            raise ValueError("El costo debe ser un número positivo")
        
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        item.costo_unitario_actual = costo
        
        # Actualizar también en inventario si existe
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        if inventario:
            inventario.ultimo_costo_unitario = costo
        
        db.commit()
        db.refresh(item)
        return item
