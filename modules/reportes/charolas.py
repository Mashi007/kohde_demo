"""
Lógica de negocio para gestión de charolas (reportes de servicio).
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Charola, CharolaItem, Item, Receta

class CharolaService:
    """Servicio para gestión de charolas."""
    
    @staticmethod
    def crear_charola(db: Session, datos: Dict) -> Charola:
        """
        Crea una nueva charola.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos de la charola
            
        Returns:
            Charola creada
        """
        # Calcular totales
        items_data = datos.get('items', [])
        total_ventas = sum(float(item.get('subtotal', 0)) for item in items_data)
        costo_total = sum(float(item.get('costo_subtotal', 0)) for item in items_data)
        ganancia = total_ventas - costo_total
        
        charola = Charola(
            numero_charola=datos.get('numero_charola', f'CH-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            fecha_servicio=datos.get('fecha_servicio', datetime.utcnow()),
            ubicacion=datos.get('ubicacion', ''),
            tiempo_comida=datos.get('tiempo_comida', 'almuerzo'),
            personas_servidas=datos.get('personas_servidas', 0),
            total_ventas=total_ventas,
            costo_total=costo_total,
            ganancia=ganancia,
            observaciones=datos.get('observaciones')
        )
        
        db.add(charola)
        db.flush()  # Para obtener el ID
        
        # Crear items de charola
        for item_data in items_data:
            charola_item = CharolaItem(
                charola_id=charola.id,
                item_id=item_data.get('item_id'),
                receta_id=item_data.get('receta_id'),
                nombre_item=item_data.get('nombre_item', ''),
                cantidad=float(item_data.get('cantidad', 0)),
                precio_unitario=float(item_data.get('precio_unitario', 0)),
                costo_unitario=float(item_data.get('costo_unitario', 0)),
                subtotal=float(item_data.get('subtotal', 0)),
                costo_subtotal=float(item_data.get('costo_subtotal', 0))
            )
            db.add(charola_item)
        
        db.commit()
        db.refresh(charola)
        return charola
    
    @staticmethod
    def obtener_charola(db: Session, charola_id: int) -> Optional[Charola]:
        """Obtiene una charola por ID."""
        return db.query(Charola).filter(Charola.id == charola_id).first()
    
    @staticmethod
    def listar_charolas(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        ubicacion: Optional[str] = None,
        tiempo_comida: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Charola]:
        """
        Lista charolas con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            ubicacion: Filtrar por ubicación
            tiempo_comida: Filtrar por tiempo de comida
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de charolas
        """
        query = db.query(Charola)
        
        if fecha_inicio:
            query = query.filter(Charola.fecha_servicio >= datetime.combine(fecha_inicio, datetime.min.time()))
        
        if fecha_fin:
            query = query.filter(Charola.fecha_servicio <= datetime.combine(fecha_fin, datetime.max.time()))
        
        if ubicacion:
            query = query.filter(Charola.ubicacion.ilike(f'%{ubicacion}%'))
        
        if tiempo_comida:
            query = query.filter(Charola.tiempo_comida == tiempo_comida)
        
        return query.order_by(Charola.fecha_servicio.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_resumen_periodo(
        db: Session,
        fecha_inicio: date,
        fecha_fin: date,
        ubicacion: Optional[str] = None
    ) -> Dict:
        """
        Obtiene un resumen de charolas en un período.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            ubicacion: Filtrar por ubicación
            
        Returns:
            Diccionario con resumen
        """
        query = db.query(Charola).filter(
            Charola.fecha_servicio >= datetime.combine(fecha_inicio, datetime.min.time()),
            Charola.fecha_servicio <= datetime.combine(fecha_fin, datetime.max.time())
        )
        
        if ubicacion:
            query = query.filter(Charola.ubicacion.ilike(f'%{ubicacion}%'))
        
        charolas = query.all()
        
        total_ventas = sum(float(c.total_ventas) for c in charolas)
        total_costos = sum(float(c.costo_total) for c in charolas)
        total_ganancia = sum(float(c.ganancia) for c in charolas)
        total_personas = sum(c.personas_servidas for c in charolas)
        
        return {
            'total_charolas': len(charolas),
            'total_ventas': total_ventas,
            'total_costos': total_costos,
            'total_ganancia': total_ganancia,
            'total_personas_servidas': total_personas,
            'ganancia_promedio': total_ganancia / len(charolas) if charolas else 0,
            'venta_promedio_por_persona': total_ventas / total_personas if total_personas > 0 else 0
        }
