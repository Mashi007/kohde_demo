"""
Lógica de negocio para gestión de mermas (pérdidas/desperdicios).
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Merma, Item
from models.merma import TipoMerma

class MermaService:
    """Servicio para gestión de mermas."""
    
    @staticmethod
    def crear_merma(db: Session, datos: Dict) -> Merma:
        """
        Crea una nueva merma.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos de la merma
            
        Returns:
            Merma creada
        """
        # Obtener item para calcular costo
        item = db.query(Item).filter(Item.id == datos['item_id']).first()
        if not item:
            raise ValueError("Item no encontrado")
        
        cantidad = float(datos.get('cantidad', 0))
        costo_unitario = float(datos.get('costo_unitario', item.costo_unitario_actual or 0))
        costo_total = cantidad * costo_unitario
        
        # Convertir tipo a enum si es string
        tipo = datos.get('tipo', 'otro')
        if isinstance(tipo, str):
            tipo = TipoMerma[tipo.upper()] if tipo.upper() in [e.name for e in TipoMerma] else TipoMerma.OTRO
        
        merma = Merma(
            item_id=datos['item_id'],
            fecha_merma=datos.get('fecha_merma', datetime.utcnow()),
            tipo=tipo,
            cantidad=cantidad,
            unidad=datos.get('unidad', item.unidad),
            costo_unitario=costo_unitario,
            costo_total=costo_total,
            motivo=datos.get('motivo'),
            ubicacion=datos.get('ubicacion'),
            registrado_por=datos.get('registrado_por')
        )
        
        db.add(merma)
        db.commit()
        db.refresh(merma)
        return merma
    
    @staticmethod
    def obtener_merma(db: Session, merma_id: int) -> Optional[Merma]:
        """Obtiene una merma por ID."""
        return db.query(Merma).filter(Merma.id == merma_id).first()
    
    @staticmethod
    def listar_mermas(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        item_id: Optional[int] = None,
        tipo: Optional[str] = None,
        ubicacion: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Merma]:
        """
        Lista mermas con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio del rango
            fecha_fin: Fecha de fin del rango
            item_id: Filtrar por item
            tipo: Filtrar por tipo de merma
            ubicacion: Filtrar por ubicación
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de mermas
        """
        query = db.query(Merma)
        
        if fecha_inicio:
            query = query.filter(Merma.fecha_merma >= datetime.combine(fecha_inicio, datetime.min.time()))
        
        if fecha_fin:
            query = query.filter(Merma.fecha_merma <= datetime.combine(fecha_fin, datetime.max.time()))
        
        if item_id:
            query = query.filter(Merma.item_id == item_id)
        
        if tipo:
            tipo_enum = TipoMerma[tipo.upper()] if tipo.upper() in [e.name for e in TipoMerma] else None
            if tipo_enum:
                query = query.filter(Merma.tipo == tipo_enum)
        
        if ubicacion:
            query = query.filter(Merma.ubicacion.ilike(f'%{ubicacion}%'))
        
        return query.order_by(Merma.fecha_merma.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_resumen_periodo(
        db: Session,
        fecha_inicio: date,
        fecha_fin: date,
        ubicacion: Optional[str] = None
    ) -> Dict:
        """
        Obtiene un resumen de mermas en un período.
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            ubicacion: Filtrar por ubicación
            
        Returns:
            Diccionario con resumen
        """
        query = db.query(Merma).filter(
            Merma.fecha_merma >= datetime.combine(fecha_inicio, datetime.min.time()),
            Merma.fecha_merma <= datetime.combine(fecha_fin, datetime.max.time())
        )
        
        if ubicacion:
            query = query.filter(Merma.ubicacion.ilike(f'%{ubicacion}%'))
        
        mermas = query.all()
        
        total_costo = sum(float(m.costo_total) for m in mermas)
        
        # Agrupar por tipo
        por_tipo = {}
        for merma in mermas:
            tipo_str = merma.tipo.value if merma.tipo else 'otro'
            if tipo_str not in por_tipo:
                por_tipo[tipo_str] = {'cantidad': 0, 'costo': 0}
            por_tipo[tipo_str]['cantidad'] += float(merma.cantidad)
            por_tipo[tipo_str]['costo'] += float(merma.costo_total)
        
        # Agrupar por item
        por_item = {}
        for merma in mermas:
            item_nombre = merma.item.nombre if merma.item else 'Desconocido'
            if item_nombre not in por_item:
                por_item[item_nombre] = {'cantidad': 0, 'costo': 0}
            por_item[item_nombre]['cantidad'] += float(merma.cantidad)
            por_item[item_nombre]['costo'] += float(merma.costo_total)
        
        return {
            'total_mermas': len(mermas),
            'total_costo': total_costo,
            'por_tipo': por_tipo,
            'por_item': por_item
        }
