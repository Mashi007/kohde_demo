"""
Lógica de negocio para gestión de inventario.
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models import Inventario, Item, Factura, FacturaItem, Requerimiento, RequerimientoItem
from utils.helpers import verificar_stock_suficiente

class InventarioService:
    """Servicio para gestión de inventario."""
    
    @staticmethod
    def obtener_inventario(db: Session, item_id: Optional[int] = None) -> List[Inventario]:
        """
        Obtiene el inventario completo o de un item específico.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item (opcional)
            
        Returns:
            Lista de registros de inventario
        """
        query = db.query(Inventario)
        
        if item_id:
            query = query.filter(Inventario.item_id == item_id)
        
        return query.all()
    
    @staticmethod
    def obtener_stock_bajo(db: Session) -> List[Dict]:
        """
        Obtiene items con stock bajo (cantidad_actual < cantidad_minima).
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Lista de items con stock bajo
        """
        try:
            items_bajo_stock = db.query(Inventario).filter(
                Inventario.cantidad_actual < Inventario.cantidad_minima
            ).all()
            
            resultado = []
            for inv in items_bajo_stock:
                try:
                    resultado.append({
                        'item_id': inv.item_id,
                        'nombre': inv.item.nombre if inv.item else 'N/A',
                        'cantidad_actual': float(inv.cantidad_actual) if inv.cantidad_actual is not None else 0.0,
                        'cantidad_minima': float(inv.cantidad_minima) if inv.cantidad_minima is not None else 0.0,
                        'unidad': inv.unidad or 'unidad',
                        'ubicacion': inv.ubicacion or 'N/A'
                    })
                except Exception as e:
                    import logging
                    logging.error(f"Error procesando inventario item_id={inv.item_id}: {str(e)}")
                    continue
            
            return resultado
        except Exception as e:
            import logging
            import traceback
            logging.error(f"Error en obtener_stock_bajo: {str(e)}")
            logging.error(traceback.format_exc())
            raise
    
    @staticmethod
    def actualizar_stock(
        db: Session,
        item_id: int,
        cantidad: float,
        operacion: str = 'entrada'  # 'entrada' o 'salida'
    ) -> Inventario:
        """
        Actualiza el stock de un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            cantidad: Cantidad a agregar o restar
            operacion: 'entrada' o 'salida'
            
        Returns:
            Inventario actualizado
        """
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        
        if not inventario:
            # Crear registro si no existe
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                raise ValueError("Item no encontrado")
            
            inventario = Inventario(
                item_id=item_id,
                cantidad_actual=0,
                unidad=item.unidad
            )
            db.add(inventario)
        
        # Actualizar cantidad
        if operacion == 'entrada':
            inventario.cantidad_actual += cantidad
        elif operacion == 'salida':
            inventario.cantidad_actual -= cantidad
            if inventario.cantidad_actual < 0:
                raise ValueError("No hay suficiente stock")
        else:
            raise ValueError("Operación inválida")
        
        db.session.commit()
        db.session.refresh(inventario)
        return inventario
    
    @staticmethod
    def verificar_disponibilidad(
        db: Session,
        item_id: int,
        cantidad_necesaria: float
    ) -> Dict:
        """
        Verifica si hay stock disponible para una cantidad necesaria.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            cantidad_necesaria: Cantidad necesaria
            
        Returns:
            Diccionario con resultado de la verificación
        """
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        
        if not inventario:
            return {
                'suficiente': False,
                'cantidad_disponible': 0,
                'cantidad_faltante': cantidad_necesaria,
                'cantidad_necesaria': cantidad_necesaria,
                'cantidad_actual': 0,
                'cantidad_minima': 0,
            }
        
        return verificar_stock_suficiente(
            cantidad_necesaria,
            float(inventario.cantidad_actual),
            float(inventario.cantidad_minima)
        )
    
    @staticmethod
    def obtener_inventario_completo_con_movimientos(db: Session) -> List[Dict]:
        """
        Obtiene el inventario completo con información de últimos movimientos.
        
        Returns:
            Lista de diccionarios con información completa del inventario
        """
        inventarios = db.query(Inventario).all()
        resultado = []
        
        for inv in inventarios:
            item_dict = inv.to_dict()
            
            # Obtener último ingreso (factura aprobada más reciente con este item)
            from models.factura import EstadoFactura, TipoFactura
            from models.requerimiento import EstadoRequerimiento
            
            ultimo_ingreso = db.query(FacturaItem).join(Factura).filter(
                FacturaItem.item_id == inv.item_id,
                Factura.estado == EstadoFactura.APROBADA,
                Factura.tipo == TipoFactura.PROVEEDOR,
                FacturaItem.cantidad_aprobada.isnot(None)
            ).order_by(desc(Factura.fecha_aprobacion)).first()
            
            # Obtener último egreso (requerimiento entregado más reciente con este item)
            ultimo_egreso = db.query(RequerimientoItem).join(Requerimiento).filter(
                RequerimientoItem.item_id == inv.item_id,
                Requerimiento.estado == EstadoRequerimiento.ENTREGADO,
                RequerimientoItem.cantidad_entregada.isnot(None)
            ).order_by(desc(Requerimiento.fecha)).first()
            
            # Calcular stock disponible (cantidad_actual - cantidad_minima)
            stock_disponible = max(0, float(inv.cantidad_actual) - float(inv.cantidad_minima))
            
            item_dict['ultimo_ingreso'] = {
                'fecha': ultimo_ingreso.factura.fecha_aprobacion.isoformat() if ultimo_ingreso and ultimo_ingreso.factura.fecha_aprobacion else None,
                'cantidad': float(ultimo_ingreso.cantidad_aprobada) if ultimo_ingreso and ultimo_ingreso.cantidad_aprobada else None,
                'factura_numero': ultimo_ingreso.factura.numero_factura if ultimo_ingreso else None,
                'proveedor': ultimo_ingreso.factura.proveedor.nombre if ultimo_ingreso and ultimo_ingreso.factura.proveedor else None,
            } if ultimo_ingreso else None
            
            item_dict['ultimo_egreso'] = {
                'fecha': ultimo_egreso.requerimiento.fecha.isoformat() if ultimo_egreso and ultimo_egreso.requerimiento.fecha else None,
                'cantidad': float(ultimo_egreso.cantidad_entregada) if ultimo_egreso and ultimo_egreso.cantidad_entregada else None,
                'requerimiento_id': ultimo_egreso.requerimiento_id if ultimo_egreso else None,
            } if ultimo_egreso else None
            
            item_dict['stock_disponible'] = stock_disponible
            item_dict['stock_seguridad'] = float(inv.cantidad_minima)
            
            resultado.append(item_dict)
        
        return resultado
    
    @staticmethod
    def obtener_resumen_dashboard(db: Session) -> Dict:
        """
        Obtiene un resumen tipo dashboard para el inventario.
        
        Returns:
            Diccionario con métricas del inventario
        """
        total_items = db.query(Inventario).count()
        items_stock_bajo = db.query(Inventario).filter(
            Inventario.cantidad_actual < Inventario.cantidad_minima
        ).count()
        
        # Calcular valor total del inventario
        inventarios = db.query(Inventario).all()
        valor_total = sum(
            float(inv.cantidad_actual) * float(inv.ultimo_costo_unitario or 0)
            for inv in inventarios
        )
        
        # Items críticos (stock muy bajo)
        items_criticos = db.query(Inventario).filter(
            Inventario.cantidad_actual < (Inventario.cantidad_minima * 0.5)
        ).count()
        
        return {
            'total_items': total_items,
            'items_stock_bajo': items_stock_bajo,
            'items_criticos': items_criticos,
            'items_stock_ok': total_items - items_stock_bajo,
            'valor_total_inventario': valor_total,
            'porcentaje_stock_bajo': round((items_stock_bajo / total_items * 100) if total_items > 0 else 0, 2),
        }
    
    @staticmethod
    def obtener_top_10_items_mas_comprados(db: Session) -> List[Dict]:
        """
        Obtiene los 10 items más comprados basado en facturas aprobadas.
        Se calcula por cantidad total comprada y frecuencia de compra.
        Los datos se actualizan automáticamente cuando se aprueban facturas.
        
        Returns:
            Lista de diccionarios con los top 10 items más comprados (silos)
        """
        import logging
        import traceback
        from models.factura import EstadoFactura, TipoFactura
        
        try:
            # Consulta para obtener los items más comprados
            # Sumamos cantidad_aprobada de facturas aprobadas de proveedores
            # Usar comparación de enums con manejo de errores
            try:
                resultado_query = db.query(
                    FacturaItem.item_id,
                    func.sum(FacturaItem.cantidad_aprobada).label('total_comprado'),
                    func.count(FacturaItem.id).label('frecuencia_compra'),
                    func.max(Factura.fecha_aprobacion).label('ultima_compra')
                ).join(Factura).filter(
                    Factura.estado == EstadoFactura.APROBADA,
                    Factura.tipo == TipoFactura.PROVEEDOR,
                    FacturaItem.item_id.isnot(None),
                    FacturaItem.cantidad_aprobada.isnot(None),
                    FacturaItem.cantidad_aprobada > 0
                ).group_by(FacturaItem.item_id).order_by(
                    func.sum(FacturaItem.cantidad_aprobada).desc()
                ).limit(10).all()
            except Exception as query_error:
                # Si falla la consulta con enums, intentar con comparación de strings
                logging.warning(f"Error en consulta con enums, intentando con strings: {str(query_error)}")
                from sqlalchemy import cast, String
                resultado_query = db.query(
                    FacturaItem.item_id,
                    func.sum(FacturaItem.cantidad_aprobada).label('total_comprado'),
                    func.count(FacturaItem.id).label('frecuencia_compra'),
                    func.max(Factura.fecha_aprobacion).label('ultima_compra')
                ).join(Factura).filter(
                    cast(Factura.estado, String) == EstadoFactura.APROBADA.name,
                    cast(Factura.tipo, String) == TipoFactura.PROVEEDOR.name,
                    FacturaItem.item_id.isnot(None),
                    FacturaItem.cantidad_aprobada.isnot(None),
                    FacturaItem.cantidad_aprobada > 0
                ).group_by(FacturaItem.item_id).order_by(
                    func.sum(FacturaItem.cantidad_aprobada).desc()
                ).limit(10).all()
            
            resultado = []
            for row in resultado_query:
                try:
                    item_id = row.item_id
                    if not item_id:
                        continue
                    
                    # Manejar valores None de forma segura
                    total_comprado = float(row.total_comprado) if row.total_comprado is not None else 0.0
                    frecuencia_compra = int(row.frecuencia_compra) if row.frecuencia_compra is not None else 0
                    ultima_compra = row.ultima_compra
                    
                    # Obtener información del inventario para este item
                    try:
                        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
                        item = db.query(Item).filter(Item.id == item_id).first()
                    except Exception as query_error:
                        logging.warning(f"Error consultando inventario/item para item_id={item_id}: {str(query_error)}")
                        continue
                    
                    if not item:
                        logging.warning(f"Item {item_id} no encontrado, saltando")
                        continue
                    
                    # Si no hay inventario, crear datos por defecto
                    if not inventario:
                        # Intentar obtener unidad del item
                        unidad = item.unidad if item.unidad else 'unidad'
                        stock_actual = 0.0
                        stock_minimo = 0.0
                    else:
                        unidad = inventario.unidad if inventario.unidad else (item.unidad if item.unidad else 'unidad')
                        # Manejar valores None de forma segura
                        stock_actual = float(inventario.cantidad_actual) if inventario.cantidad_actual is not None else 0.0
                        stock_minimo = float(inventario.cantidad_minima) if inventario.cantidad_minima is not None else 0.0
                    
                    # Validar que los valores sean números válidos
                    if not isinstance(stock_actual, (int, float)) or not isinstance(stock_minimo, (int, float)):
                        logging.warning(f"Valores inválidos para item_id={item_id}: stock_actual={stock_actual}, stock_minimo={stock_minimo}")
                        stock_actual = 0.0
                        stock_minimo = 0.0
                    
                    # Calcular porcentaje de llenado del silo
                    # El "silo" se llena hasta el stock mínimo, luego el exceso
                    # Usamos el stock mínimo como referencia base para el 100%
                    if stock_minimo > 0:
                        nivel_maximo = max(stock_minimo * 2, stock_actual)
                    else:
                        nivel_maximo = max(stock_actual, 1.0)
                    
                    nivel_llenado = (stock_actual / nivel_maximo * 100) if nivel_maximo > 0 else 0.0
                    porcentaje_minimo = (stock_minimo / nivel_maximo * 100) if nivel_maximo > 0 else 0.0
                    
                    # Determinar estado
                    if stock_minimo > 0:
                        if stock_actual < stock_minimo * 0.5:
                            estado = 'critico'
                        elif stock_actual < stock_minimo:
                            estado = 'bajo'
                        else:
                            estado = 'ok'
                    else:
                        estado = 'ok' if stock_actual > 0 else 'sin_stock'
                    
                    # Formatear fecha de última compra
                    ultima_compra_str = None
                    if ultima_compra:
                        try:
                            if hasattr(ultima_compra, 'isoformat'):
                                ultima_compra_str = ultima_compra.isoformat()
                            else:
                                ultima_compra_str = str(ultima_compra)
                        except Exception as date_error:
                            logging.warning(f"Error formateando fecha de última compra: {str(date_error)}")
                            ultima_compra_str = None
                    
                    resultado.append({
                        'item_id': item_id,
                        'item_nombre': item.nombre if item.nombre else f'Item {item_id}',
                        'unidad': unidad,
                        'stock_total': round(stock_actual, 2),
                        'stock_minimo': round(stock_minimo, 2),
                        'stock_disponible': round(max(0, stock_actual - stock_minimo), 2),
                        'total_comprado': round(total_comprado, 2),
                        'frecuencia_compra': frecuencia_compra,
                        'ultima_compra': ultima_compra_str,
                        'porcentaje_minimo': round(porcentaje_minimo, 1),
                        'nivel_llenado': round(nivel_llenado, 1),
                        'estado': estado,
                    })
                except Exception as row_error:
                    logging.error(f"Error procesando fila en obtener_top_10_items_mas_comprados: {str(row_error)}")
                    logging.error(traceback.format_exc())
                    # Continuar con la siguiente fila
                    continue
            
            return resultado
            
        except Exception as e:
            logging.error(f"Error crítico en obtener_top_10_items_mas_comprados: {str(e)}")
            logging.error(traceback.format_exc())
            # Retornar lista vacía en lugar de lanzar excepción para evitar error 500
            return []