"""
Lógica de negocio para programación de menús.
"""
from typing import List, Optional, Dict
from datetime import date, datetime
from sqlalchemy.orm import Session
from models import ProgramacionMenu, ProgramacionMenuItem, Receta, Inventario
from modules.logistica.inventario import InventarioService
from modules.logistica.pedidos import PedidoCompraService

class ProgramacionMenuService:
    """Servicio para gestión de programación de menús."""
    
    @staticmethod
    def crear_programacion(db: Session, datos: Dict) -> ProgramacionMenu:
        """
        Crea una nueva programación de menú.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos de la programación
            
        Returns:
            Programación creada
        """
        recetas_data = datos.pop('recetas', [])
        
        programacion = ProgramacionMenu(**datos)
        db.add(programacion)
        db.flush()  # Para obtener el ID
        
        # Crear items de programación (recetas)
        for receta_data in recetas_data:
            receta = db.query(Receta).filter(Receta.id == receta_data['receta_id']).first()
            if not receta:
                raise ValueError(f"Receta {receta_data['receta_id']} no encontrada")
            
            programacion_item = ProgramacionMenuItem(
                programacion_id=programacion.id,
                receta_id=receta.id,
                cantidad_porciones=int(receta_data['cantidad_porciones'])
            )
            db.add(programacion_item)
        
        db.commit()
        db.refresh(programacion)
        return programacion
    
    @staticmethod
    def actualizar_programacion(db: Session, programacion_id: int, datos: Dict) -> ProgramacionMenu:
        """
        Actualiza una programación de menú existente.
        
        Args:
            db: Sesión de base de datos
            programacion_id: ID de la programación a actualizar
            datos: Diccionario con datos actualizados
            
        Returns:
            Programación actualizada
        """
        programacion = db.query(ProgramacionMenu).filter(
            ProgramacionMenu.id == programacion_id
        ).first()
        
        if not programacion:
            raise ValueError("Programación no encontrada")
        
        recetas_data = datos.pop('recetas', None)
        
        # Actualizar campos básicos
        for key, value in datos.items():
            if hasattr(programacion, key):
                setattr(programacion, key, value)
        
        # Actualizar recetas si se proporcionan
        if recetas_data is not None:
            # Eliminar items existentes
            db.query(ProgramacionMenuItem).filter(
                ProgramacionMenuItem.programacion_id == programacion_id
            ).delete()
            
            # Crear nuevos items
            for receta_data in recetas_data:
                receta = db.query(Receta).filter(Receta.id == receta_data['receta_id']).first()
                if not receta:
                    raise ValueError(f"Receta {receta_data['receta_id']} no encontrada")
                
                programacion_item = ProgramacionMenuItem(
                    programacion_id=programacion.id,
                    receta_id=receta.id,
                    cantidad_porciones=int(receta_data['cantidad_porciones'])
                )
                db.add(programacion_item)
        
        db.commit()
        db.refresh(programacion)
        return programacion
    
    @staticmethod
    def calcular_necesidades(db: Session, programacion_id: int) -> Dict:
        """
        Calcula las necesidades de items para una programación.
        
        Args:
            db: Sesión de base de datos
            programacion_id: ID de la programación
            
        Returns:
            Diccionario con necesidades calculadas
        """
        programacion = db.query(ProgramacionMenu).filter(
            ProgramacionMenu.id == programacion_id
        ).first()
        
        if not programacion:
            raise ValueError("Programación no encontrada")
        
        necesidades = programacion.calcular_necesidades_items()
        
        # Verificar disponibilidad en inventario
        items_faltantes = []
        items_suficientes = []
        
        for item_id, cantidad_necesaria in necesidades.items():
            disponibilidad = InventarioService.verificar_disponibilidad(db, item_id, cantidad_necesaria)
            
            from models import Item as ItemModel
            item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
            
            item_info = {
                'item_id': item_id,
                'nombre': item.nombre if item else 'N/A',
                'cantidad_necesaria': cantidad_necesaria,
                'cantidad_disponible': disponibilidad['cantidad_disponible'],
                'cantidad_actual': disponibilidad['cantidad_actual'],
                'cantidad_faltante': disponibilidad['cantidad_faltante'],
                'unidad': item.unidad if item else 'N/A'
            }
            
            if disponibilidad['suficiente']:
                items_suficientes.append(item_info)
            else:
                items_faltantes.append(item_info)
        
        return {
            'programacion_id': programacion_id,
            'fecha': programacion.fecha.isoformat(),
            'items_suficientes': items_suficientes,
            'items_faltantes': items_faltantes,
            'necesidades_totales': necesidades
        }
    
    @staticmethod
    def generar_pedidos_automaticos(
        db: Session,
        programacion_id: int,
        usuario_id: int
    ) -> List[Dict]:
        """
        Genera pedidos automáticos para items faltantes de una programación.
        
        Args:
            db: Sesión de base de datos
            programacion_id: ID de la programación
            usuario_id: ID del usuario que genera los pedidos
            
        Returns:
            Lista de pedidos creados
        """
        necesidades = ProgramacionMenuService.calcular_necesidades(db, programacion_id)
        
        items_faltantes = necesidades['items_faltantes']
        
        if not items_faltantes:
            return []
        
        # Preparar items para pedido automático (agregar amortiguador)
        from config import Config
        items_para_pedido = []
        
        for item in items_faltantes:
            cantidad_faltante = item['cantidad_faltante']
            # Agregar amortiguador (20% adicional)
            cantidad_con_amortiguador = cantidad_faltante * (1 + Config.STOCK_MINIMUM_THRESHOLD_PERCENTAGE)
            
            items_para_pedido.append({
                'item_id': item['item_id'],
                'cantidad': cantidad_con_amortiguador
            })
        
        # Generar pedidos automáticos
        pedidos = PedidoCompraService.generar_pedido_automatico(
            db,
            items_para_pedido,
            usuario_id
        )
        
        return [pedido.to_dict() for pedido in pedidos]
    
    @staticmethod
    def listar_programaciones(
        db: Session,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        ubicacion: Optional[str] = None,
        tiempo_comida: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProgramacionMenu]:
        """
        Lista programaciones con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            fecha_desde: Filtrar desde fecha
            fecha_hasta: Filtrar hasta fecha
            ubicacion: Filtrar por ubicación
            tiempo_comida: Filtrar por tiempo de comida (desayuno, almuerzo, cena)
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de programaciones
        """
        from models.programacion import TiempoComida
        
        query = db.query(ProgramacionMenu)
        
        if fecha_desde:
            query = query.filter(ProgramacionMenu.fecha >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(ProgramacionMenu.fecha <= fecha_hasta)
        
        if ubicacion:
            query = query.filter(ProgramacionMenu.ubicacion == ubicacion)
        
        if tiempo_comida:
            try:
                tiempo_enum = TiempoComida[tiempo_comida.upper()]
                query = query.filter(ProgramacionMenu.tiempo_comida == tiempo_enum)
            except KeyError:
                pass  # Ignorar si el valor no es válido
        
        return query.order_by(ProgramacionMenu.fecha.desc(), ProgramacionMenu.tiempo_comida).offset(skip).limit(limit).all()
