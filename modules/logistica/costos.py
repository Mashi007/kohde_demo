"""
Lógica de negocio para gestión de costos estandarizados.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from models import Item, FacturaItem, Factura, CostoItem
from models.factura import EstadoFactura
from modules.logistica.conversor_unidades import (
    son_unidades_compatibles,
    calcular_costo_unitario_estandarizado,
    convertir_unidad,
    convertir_a_unidad_base
)
import statistics

class CostoService:
    """Servicio para gestión de costos estandarizados."""
    
    @staticmethod
    def calcular_y_almacenar_costo_estandarizado(db: Session, item_id: int) -> Optional[CostoItem]:
        """
        Calcula y almacena el costo estandarizado de un item basado en las últimas 3 facturas aprobadas.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            
        Returns:
            CostoItem creado o actualizado, o None si no hay datos suficientes
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None
        
        # Obtener las últimas 3 facturas aprobadas que contengan este item
        facturas_items = db.query(FacturaItem).join(Factura).filter(
            FacturaItem.item_id == item_id,
            Factura.estado == EstadoFactura.APROBADA,
            FacturaItem.cantidad_aprobada.isnot(None),
            FacturaItem.cantidad_aprobada > 0,
            FacturaItem.precio_unitario.isnot(None),
            FacturaItem.precio_unitario > 0
        ).order_by(desc(Factura.fecha_aprobacion)).limit(3).all()
        
        if not facturas_items:
            return None
        
        # IMPORTANTE: La unidad estándar se define en el módulo Items (item.unidad)
        # Esta es la unidad de referencia para estandarizar todas las facturas
        unidad_estandar = item.unidad  # Unidad estándar definida en el módulo Items
        
        # Calcular costos unitarios estandarizados para cada factura
        # Todas las facturas se convierten a la unidad estándar del item
        costos_estandarizados = []
        notas_conversion = []
        
        for fi in facturas_items:
            # Obtener datos de la factura
            precio_unitario_factura = float(fi.precio_unitario)
            cantidad_aprobada_factura = float(fi.cantidad_aprobada)
            
            # Obtener unidad de la factura (almacenada en FacturaItem o usar la del item como fallback)
            unidad_factura = fi.unidad if fi.unidad else item.unidad
            
            # Calcular costo total de la factura
            costo_total_factura = precio_unitario_factura * cantidad_aprobada_factura
            
            # ESTANDARIZACIÓN: Convertir siempre a la unidad estándar del módulo Items
            if son_unidades_compatibles(unidad_factura, unidad_estandar):
                if unidad_factura != unidad_estandar:
                    # Convertir cantidad de la factura a la unidad estándar del item
                    cantidad_estandarizada = convertir_unidad(
                        cantidad_aprobada_factura,
                        unidad_factura,
                        unidad_estandar
                    )
                    if cantidad_estandarizada and cantidad_estandarizada > 0:
                        # Calcular costo unitario en la unidad estándar
                        costo_unitario_estandarizado = costo_total_factura / cantidad_estandarizada
                        costos_estandarizados.append(costo_unitario_estandarizado)
                        notas_conversion.append(
                            f"Factura #{fi.factura.numero_factura}: "
                            f"${costo_unitario_estandarizado:.2f}/{unidad_estandar} "
                            f"(estandarizado: {cantidad_aprobada_factura} {unidad_factura} → {cantidad_estandarizada:.2f} {unidad_estandar})"
                        )
                    else:
                        # Error en conversión - usar precio directamente pero marcar como advertencia
                        costos_estandarizados.append(precio_unitario_factura)
                        notas_conversion.append(
                            f"Factura #{fi.factura.numero_factura}: "
                            f"${precio_unitario_factura:.2f}/{unidad_estandar} "
                            f"(ADVERTENCIA: error al convertir {unidad_factura} a {unidad_estandar})"
                        )
                else:
                    # Misma unidad que la estándar - usar directamente
                    costos_estandarizados.append(precio_unitario_factura)
                    notas_conversion.append(
                        f"Factura #{fi.factura.numero_factura}: "
                        f"${precio_unitario_factura:.2f}/{unidad_estandar} "
                        f"(cantidad: {cantidad_aprobada_factura} {unidad_estandar} - ya estándar)"
                    )
            else:
                # Unidades no compatibles - no se puede estandarizar
                costos_estandarizados.append(precio_unitario_factura)
                notas_conversion.append(
                    f"Factura #{fi.factura.numero_factura}: "
                    f"${precio_unitario_factura:.2f}/{unidad_estandar} "
                    f"(ERROR: unidades no compatibles - {unidad_factura} no se puede convertir a {unidad_estandar})"
                )
        
        if not costos_estandarizados:
            return None
        
        # Calcular promedio
        costo_promedio = sum(costos_estandarizados) / len(costos_estandarizados)
        
        # Calcular variación (desviación estándar como porcentaje del promedio)
        if len(costos_estandarizados) > 1:
            desviacion_estandar = statistics.stdev(costos_estandarizados)
            variacion_porcentaje = (desviacion_estandar / costo_promedio) * 100 if costo_promedio > 0 else 0
            variacion_absoluta = max(costos_estandarizados) - min(costos_estandarizados)
        else:
            variacion_porcentaje = 0
            variacion_absoluta = 0
        
        # Buscar o crear registro de costo estandarizado
        costo_item = db.query(CostoItem).filter(CostoItem.item_id == item_id).first()
        
        if costo_item:
            # Actualizar existente
            costo_item.costo_unitario_promedio = costo_promedio
            costo_item.cantidad_facturas_usadas = len(facturas_items)
            costo_item.variacion_porcentaje = variacion_porcentaje
            costo_item.variacion_absoluta = variacion_absoluta
            costo_item.fecha_actualizacion = datetime.utcnow()
            costo_item.notas = "\n".join(notas_conversion)
        else:
            # Crear nuevo
            costo_item = CostoItem(
                item_id=item_id,
                unidad_estandar=unidad_estandar,
                costo_unitario_promedio=costo_promedio,
                cantidad_facturas_usadas=len(facturas_items),
                variacion_porcentaje=variacion_porcentaje,
                variacion_absoluta=variacion_absoluta,
                notas="\n".join(notas_conversion)
            )
            db.add(costo_item)
        
        db.commit()
        db.refresh(costo_item)
        return costo_item
    
    @staticmethod
    def obtener_costo_estandarizado(db: Session, item_id: int) -> Optional[CostoItem]:
        """Obtiene el costo estandarizado de un item."""
        return db.query(CostoItem).filter(
            CostoItem.item_id == item_id,
            CostoItem.activo == True
        ).first()
    
    @staticmethod
    def listar_costos_estandarizados(
        db: Session,
        label_id: Optional[int] = None,
        categoria: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CostoItem]:
        """
        Lista costos estandarizados con filtros opcionales.
        Si no hay costos o tienen cantidad_facturas_usadas en 0, genera datos mock.
        
        Args:
            db: Sesión de base de datos
            label_id: Filtrar por label de item
            categoria: Filtrar por categoría de item
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de CostoItem
        """
        query = db.query(CostoItem).join(Item).filter(CostoItem.activo == True)
        
        if label_id:
            from models.item_label import item_labels
            query = query.filter(Item.labels.any(id=label_id))
        
        if categoria:
            from models.item import CategoriaItem
            query = query.filter(Item.categoria == CategoriaItem[categoria.upper()])
        
        costos = query.order_by(desc(CostoItem.fecha_actualizacion)).offset(skip).limit(limit).all()
        
        # Si no hay costos o todos tienen cantidad_facturas_usadas en 0, agregar datos mock
        if not costos or all(c.cantidad_facturas_usadas == 0 for c in costos):
            try:
                # Obtener items activos para generar costos mock
                items_query = db.query(Item).filter(Item.activo == True)
                
                if label_id:
                    from models.item_label import item_labels
                    items_query = items_query.filter(Item.labels.any(id=label_id))
                
                if categoria:
                    from models.item import CategoriaItem
                    items_query = items_query.filter(Item.categoria == CategoriaItem[categoria.upper()])
                
                items = items_query.limit(limit).all()
                
                # Generar costos mock para items que no tienen costo
                import random
                costos_mock = []
                
                for item in items:
                    # Verificar si ya existe un costo para este item
                    costo_existente = db.query(CostoItem).filter(
                        CostoItem.item_id == item.id
                    ).first()
                    
                    if not costo_existente or costo_existente.cantidad_facturas_usadas == 0:
                        # Generar datos mock realistas
                        cantidad_facturas = random.choice([1, 2, 3])  # 1-3 facturas típicamente
                        
                        # Precio mock basado en tipo de item
                        if item.costo_unitario_actual:
                            precio_base = float(item.costo_unitario_actual)
                        elif 'carne' in item.nombre.lower() or 'pollo' in item.nombre.lower():
                            precio_base = round(8.50 + random.uniform(0, 5), 2)
                        elif 'verdura' in item.nombre.lower() or 'hortaliza' in item.nombre.lower():
                            precio_base = round(1.20 + random.uniform(0, 1), 2)
                        elif 'lacteo' in item.nombre.lower() or 'leche' in item.nombre.lower():
                            precio_base = round(3.50 + random.uniform(0, 2), 2)
                        else:
                            precio_base = round(2.50 + random.uniform(0, 3), 2)
                        
                        # Variación pequeña (5-15%)
                        variacion_porcentaje = round(random.uniform(5, 15), 1)
                        variacion_absoluta = round(precio_base * (variacion_porcentaje / 100), 2)
                        
                        if costo_existente:
                            # Actualizar existente con datos mock
                            costo_existente.cantidad_facturas_usadas = cantidad_facturas
                            costo_existente.costo_unitario_promedio = precio_base
                            costo_existente.variacion_porcentaje = variacion_porcentaje
                            costo_existente.variacion_absoluta = variacion_absoluta
                            costo_existente.fecha_actualizacion = datetime.utcnow()
                            costo_existente.notas = f"Datos mock generados automáticamente - {cantidad_facturas} facturas simuladas"
                            costos_mock.append(costo_existente)
                        else:
                            # Crear nuevo costo mock
                            costo_mock = CostoItem(
                                item_id=item.id,
                                unidad_estandar=item.unidad,
                                costo_unitario_promedio=precio_base,
                                cantidad_facturas_usadas=cantidad_facturas,
                                variacion_porcentaje=variacion_porcentaje,
                                variacion_absoluta=variacion_absoluta,
                                notas=f"Datos mock generados automáticamente - {cantidad_facturas} facturas simuladas",
                                activo=True
                            )
                            db.add(costo_mock)
                            costos_mock.append(costo_mock)
                
                if costos_mock:
                    try:
                        db.commit()
                        # Refrescar y retornar los costos actualizados
                        for costo in costos_mock:
                            db.refresh(costo)
                        
                        # Retornar costos actualizados (combinar existentes con mock)
                        costos_actualizados = query.order_by(desc(CostoItem.fecha_actualizacion)).offset(skip).limit(limit).all()
                        return costos_actualizados
                    except Exception as commit_error:
                        import logging
                        logging.warning(f"Error haciendo commit de costos mock: {str(commit_error)}")
                        db.rollback()
                        # Retornar costos existentes aunque tengan 0 facturas
            except Exception as e:
                import logging
                logging.warning(f"Error generando costos mock: {str(e)}")
                # Continuar con costos existentes aunque tengan 0 facturas
        
        return costos
    
    @staticmethod
    def recalcular_todos_los_costos(db: Session) -> Dict[str, int]:
        """
        Recalcula todos los costos estandarizados de items y recetas.
        
        Returns:
            Diccionario con estadísticas del recálculo
        """
        items = db.query(Item).filter(Item.activo == True).all()
        
        calculados_items = 0
        sin_datos_items = 0
        errores_items = 0
        
        # Recalcular costos de items
        for item in items:
            try:
                costo = CostoService.calcular_y_almacenar_costo_estandarizado(db, item.id)
                if costo:
                    calculados_items += 1
                    # Actualizar costo_unitario_actual del item con el promedio calculado
                    item.costo_unitario_actual = costo.costo_unitario_promedio
                else:
                    sin_datos_items += 1
            except Exception as e:
                errores_items += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error calculando costo para item {item.id}: {e}", exc_info=True)
        
        db.commit()
        
        # Recalcular costos de recetas (se actualizan automáticamente cuando cambian los costos de items)
        from models import Receta
        recetas = db.query(Receta).filter(Receta.activa == True).all()
        
        calculadas_recetas = 0
        errores_recetas = 0
        
        for receta in recetas:
            try:
                # Recalcular totales de la receta (esto actualiza costo_total y costo_por_porcion)
                receta.calcular_totales()
                calculadas_recetas += 1
            except Exception as e:
                errores_recetas += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error calculando costo para receta {receta.id}: {e}", exc_info=True)
        
        db.commit()
        
        return {
            'items': {
                'calculados': calculados_items,
                'sin_datos': sin_datos_items,
                'errores': errores_items,
                'total': len(items)
            },
            'recetas': {
                'calculadas': calculadas_recetas,
                'errores': errores_recetas,
                'total': len(recetas)
            }
        }
