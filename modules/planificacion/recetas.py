"""
Lógica de negocio para gestión de recetas.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from models import Receta, RecetaIngrediente, Item

class RecetaService:
    """Servicio para gestión de recetas."""
    
    @staticmethod
    def crear_receta(db: Session, datos: Dict) -> Receta:
        """
        Crea una nueva receta con sus ingredientes.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos de la receta
            
        Returns:
            Receta creada
        """
        ingredientes_data = datos.pop('ingredientes', [])
        
        # Convertir tipo string a enum si es necesario
        if isinstance(datos.get('tipo'), str):
            from models.receta import TipoReceta
            tipo_str = datos['tipo'].lower().strip()  # Convertir a minúsculas y limpiar
            
            # Mapeo directo de valores a enums
            tipo_map = {
                'desayuno': TipoReceta.DESAYUNO,
                'almuerzo': TipoReceta.ALMUERZO,
                'cena': TipoReceta.CENA,
            }
            
            # Buscar el enum por su valor
            tipo_enum = tipo_map.get(tipo_str)
            if tipo_enum is None:
                # Si no se encuentra, intentar por nombre del enum (fallback)
                try:
                    tipo_enum = TipoReceta[tipo_str.upper()]
                except KeyError:
                    tipo_enum = TipoReceta.ALMUERZO  # Valor por defecto
            
            datos['tipo'] = tipo_enum
        
        receta = Receta(**datos)
        db.add(receta)
        db.flush()  # Para obtener el ID
        
        # Crear ingredientes
        for ing_data in ingredientes_data:
            item = db.query(Item).filter(Item.id == ing_data['item_id']).first()
            if not item:
                raise ValueError(f"Item {ing_data['item_id']} no encontrado")
            
            ingrediente = RecetaIngrediente(
                receta_id=receta.id,
                item_id=item.id,
                cantidad=float(ing_data['cantidad']),
                unidad=ing_data.get('unidad', item.unidad)
            )
            db.add(ingrediente)
        
        # Calcular totales
        receta.calcular_totales()
        
        db.commit()
        db.refresh(receta)
        return receta
    
    @staticmethod
    def obtener_receta(db: Session, receta_id: int) -> Optional[Receta]:
        """Obtiene una receta por ID."""
        return db.query(Receta).filter(Receta.id == receta_id).first()
    
    @staticmethod
    def listar_recetas(
        db: Session,
        activa: Optional[bool] = None,
        tipo: Optional[str] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Receta]:
        """
        Lista recetas con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            activa: Filtrar por estado activa
            tipo: Filtrar por tipo (desayuno, almuerzo, cena)
            busqueda: Búsqueda por nombre
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de recetas
        """
        from sqlalchemy import or_
        from sqlalchemy.orm import selectinload, joinedload
        from models.receta import TipoReceta
        
        # Usar selectinload para cargar ingredientes y joinedload para items
        # Esto evita problemas de lazy loading cuando la sesión está cerrada
        # Nota: selectinload para ingredientes (uno a muchos) y joinedload para item (muchos a uno)
        # IMPORTANTE: Usar referencia directa a la clase, no strings
        try:
            query = db.query(Receta).options(
                selectinload(Receta.ingredientes).joinedload(RecetaIngrediente.item)
            )
        except Exception as e:
            # Si hay un error con el eager loading, usar query básico
            import logging
            logging.warning(f"Error en eager loading, usando query básico: {str(e)}")
            query = db.query(Receta)
        
        if activa is not None:
            query = query.filter(Receta.activa == activa)
        
        if tipo:
            try:
                tipo_enum = TipoReceta[tipo.upper()]
                query = query.filter(Receta.tipo == tipo_enum)
            except KeyError:
                pass  # Tipo inválido, ignorar filtro
        
        if busqueda:
            query = query.filter(Receta.nombre.ilike(f'%{busqueda}%'))
        
        return query.order_by(Receta.nombre).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_receta(db: Session, receta_id: int, datos: Dict) -> Receta:
        """
        Actualiza una receta existente.
        
        Args:
            db: Sesión de base de datos
            receta_id: ID de la receta
            datos: Datos a actualizar
            
        Returns:
            Receta actualizada
        """
        receta = RecetaService.obtener_receta(db, receta_id)
        if not receta:
            raise ValueError("Receta no encontrada")
        
        # Si se actualizan ingredientes, eliminar los antiguos y crear nuevos
        if 'ingredientes' in datos:
            # Eliminar ingredientes existentes
            db.query(RecetaIngrediente).filter(
                RecetaIngrediente.receta_id == receta_id
            ).delete()
            
            # Crear nuevos ingredientes
            for ing_data in datos['ingredientes']:
                ingrediente = RecetaIngrediente(
                    receta_id=receta_id,
                    item_id=ing_data['item_id'],
                    cantidad=float(ing_data['cantidad']),
                    unidad=ing_data.get('unidad', 'unidad')
                )
                db.add(ingrediente)
            
            datos.pop('ingredientes')
        
        # Convertir tipo string a enum si es necesario
        if isinstance(datos.get('tipo'), str):
            from models.receta import TipoReceta
            tipo_str = datos['tipo'].lower().strip()  # Convertir a minúsculas y limpiar
            
            # Mapeo directo de valores a enums
            tipo_map = {
                'desayuno': TipoReceta.DESAYUNO,
                'almuerzo': TipoReceta.ALMUERZO,
                'cena': TipoReceta.CENA,
            }
            
            # Buscar el enum por su valor
            tipo_enum = tipo_map.get(tipo_str)
            if tipo_enum is None:
                # Si no se encuentra, intentar por nombre del enum (fallback)
                try:
                    tipo_enum = TipoReceta[tipo_str.upper()]
                except KeyError:
                    tipo_enum = TipoReceta.ALMUERZO  # Valor por defecto
            
            datos['tipo'] = tipo_enum
        
        # Actualizar otros campos
        for key, value in datos.items():
            if hasattr(receta, key) and key != 'id':
                setattr(receta, key, value)
        
        # Recalcular totales
        receta.calcular_totales()
        
        db.commit()
        db.refresh(receta)
        return receta
    
    @staticmethod
    def duplicar_receta(db: Session, receta_id: int, nuevo_nombre: str) -> Receta:
        """
        Duplica una receta existente.
        
        Args:
            db: Sesión de base de datos
            receta_id: ID de la receta a duplicar
            nuevo_nombre: Nombre para la nueva receta
            
        Returns:
            Receta duplicada
        """
        receta_original = RecetaService.obtener_receta(db, receta_id)
        if not receta_original:
            raise ValueError("Receta no encontrada")
        
        datos = receta_original.to_dict()
        datos['nombre'] = nuevo_nombre
        datos['ingredientes'] = [
            {
                'item_id': ing.item_id,
                'cantidad': float(ing.cantidad),
                'unidad': ing.unidad
            }
            for ing in receta_original.ingredientes
        ]
        
        return RecetaService.crear_receta(db, datos)
