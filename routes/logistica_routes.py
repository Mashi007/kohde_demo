"""
Rutas API para módulo de Logística.
Incluye: Items, Inventario, Facturas, Compras y Pedidos
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from sqlalchemy import and_, exists
from models import db
from utils.route_helpers import (
    handle_db_transaction, parse_date, parse_datetime, require_field,
    validate_positive_int, validate_file_upload, success_response,
    error_response, paginated_response
)
from modules.logistica.items import ItemService
from modules.logistica.inventario import InventarioService
from modules.logistica.requerimientos import RequerimientoService
from modules.logistica.facturas import FacturaService
from modules.logistica.pedidos import PedidoCompraService
from modules.logistica.pedidos_internos import PedidoInternoService
from modules.logistica.compras_stats import ComprasStatsService
from modules.logistica.costos import CostoService
from models import ItemLabel, Factura, FacturaItem, Receta, Proveedor
from models.item import Item
from models.factura import EstadoFactura, TipoFactura
from models.requerimiento import EstadoRequerimiento
from models.receta import TipoReceta
from modules.logistica.pedidos_automaticos import PedidosAutomaticosService
from modules.planificacion.requerimientos import RequerimientosService
from config import Config
from datetime import datetime

bp = Blueprint('logistica', __name__)

# ========== RUTAS DE ITEMS ==========

@bp.route('/items/health', methods=['GET'])
def health_check_items():
    """Endpoint de diagnóstico para verificar el estado del módulo de items."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        health_info = {
            'tabla_items_existe': 'items' in tables,
            'tabla_item_labels_existe': 'item_labels' in tables,
            'tabla_item_label_existe': 'item_label' in tables,
            'sesion_activa': db.session.is_active,
            'total_items': 0,
            'items_activos': 0,
        }
        
        if 'items' in tables:
            try:
                total = db.session.query(Item).count()
                activos = db.session.query(Item).filter(Item.activo == True).count()
                health_info['total_items'] = total
                health_info['items_activos'] = activos
            except Exception as e:
                health_info['error_contando_items'] = str(e)
        
        return jsonify({
            'status': 'ok',
            'health': health_info
        }), 200
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@bp.route('/items', methods=['GET'])
def listar_items():
    """Lista items con filtros opcionales."""
    import logging
    try:
        categoria = request.args.get('categoria')
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        activo_bool = None if activo is None else activo.lower() == 'true'
        
        # Verificar que la sesión esté activa antes de hacer queries
        try:
            if not db.session.is_active:
                db.session.rollback()
        except Exception as session_error:
            logging.warning(f"Error verificando sesión: {str(session_error)}")
            # Intentar crear nueva sesión si es necesario
            try:
                db.session.expire_all()
            except:
                pass
        
        # Verificar si hay items, si no hay y no hay filtros, generar datos mock
        total_items = db.session.query(Item).count()
        if total_items == 0 and not categoria and not busqueda:
            try:
                logging.info("No hay items, generando datos mock...")
                # Verificar y crear proveedores si no existen
                proveedores = db.session.query(Proveedor).all()
                if not proveedores:
                    from scripts.init_mock_data import init_proveedores
                    proveedores = init_proveedores()
                # Verificar y crear labels si no existen
                from models.item import ItemLabel
                labels = db.session.query(ItemLabel).all()
                if not labels:
                    from scripts.init_food_labels import init_food_labels
                    init_food_labels()
                    labels = db.session.query(ItemLabel).all()
                # Crear items usando el script independiente que maneja sus propias dependencias
                if proveedores and labels:
                    from scripts.init_items import init_items
                    init_items()
            except Exception as mock_error:
                logging.warning(f"Error generando items mock: {str(mock_error)}")
        
        # Obtener items con eager loading de labels para evitar problemas de lazy loading
        try:
            items = ItemService.listar_items(
                db.session,
                categoria=categoria,
                activo=activo_bool,
                busqueda=busqueda,
                skip=skip,
                limit=limit
            )
        except Exception as query_error:
            import logging
            import traceback
            logging.error(f"Error en query de items: {str(query_error)}")
            logging.error(traceback.format_exc())
            # Intentar rollback y retornar lista vacía
            try:
                db.session.rollback()
            except:
                pass
            return paginated_response([], skip=skip, limit=limit)
        
        # Si no hay items, retornar lista vacía directamente
        if not items:
            return paginated_response([], skip=skip, limit=limit)
        
        # Agregar costo promedio calculado a cada item
        items_con_costo = []
        for item in items:
            try:
                # Asegurar que la sesión esté activa antes de procesar cada item
                if not db.session.is_active:
                    try:
                        db.session.rollback()
                    except:
                        pass
                
                # Asegurar que las relaciones estén cargadas antes de serializar
                # Esto evita problemas con sesiones cerradas
                try:
                    # Verificar si labels está cargado (con eager loading debería estar)
                    if hasattr(item, 'labels'):
                        _ = item.labels  # Forzar carga de labels si es necesario
                except Exception as label_error:
                    import logging
                    logging.warning(f"Error accediendo labels del item {item.id}: {str(label_error)}")
                    # Si falla, continuar sin labels
                
                # Intentar serializar el item primero
                item_dict = item.to_dict()
                
                # Calcular costo promedio (puede retornar None si hay error)
                try:
                    # Verificar que la sesión esté activa antes de calcular costo
                    if db.session.is_active:
                        costo_promedio = ItemService.calcular_costo_unitario_promedio(db.session, item.id)
                        item_dict['costo_unitario_promedio'] = costo_promedio
                    else:
                        item_dict['costo_unitario_promedio'] = None
                except Exception as costo_error:
                    import logging
                    import traceback
                    logging.warning(f"Error calculando costo promedio para item {item.id}: {str(costo_error)}")
                    logging.debug(traceback.format_exc())
                    # Hacer rollback y continuar sin costo promedio
                    try:
                        if db.session.is_active:
                            db.session.rollback()
                    except:
                        pass
                    item_dict['costo_unitario_promedio'] = None
                
                items_con_costo.append(item_dict)
            except Exception as e:
                import logging
                import traceback
                logging.error(f"Error procesando item {item.id}: {str(e)}")
                logging.error(traceback.format_exc())
                
                # Intentar agregar el item sin costo promedio y sin labels
                try:
                    # Hacer rollback de la transacción si hay error
                    try:
                        db.session.rollback()
                    except:
                        pass
                    
                    # Manejar categoria que puede ser string (PG_ENUM) o enum
                    categoria_value = None
                    if item.categoria:
                        if isinstance(item.categoria, str):
                            categoria_value = item.categoria.lower()
                        elif hasattr(item.categoria, 'value'):
                            categoria_value = item.categoria.value
                        else:
                            categoria_value = str(item.categoria).lower()
                    
                    item_dict = {
                        'id': item.id,
                        'codigo': item.codigo,
                        'nombre': item.nombre,
                        'descripcion': item.descripcion,
                        'categoria': categoria_value,
                        'unidad': item.unidad,
                        'calorias_por_unidad': float(item.calorias_por_unidad) if item.calorias_por_unidad else None,
                        'costo_unitario_actual': float(item.costo_unitario_actual) if item.costo_unitario_actual else None,
                        'activo': item.activo,
                        'labels': [],
                        'costo_unitario_promedio': None,
                    }
                    items_con_costo.append(item_dict)
                except Exception as e2:
                    logging.error(f"Error crítico serializando item {item.id}: {str(e2)}")
                    # Continuar con el siguiente item sin agregar este
                    continue
        
        # Si no hay items procesados pero había items en la query, puede ser un problema de serialización
        # En ese caso, retornar lista vacía en lugar de error para evitar 500
        if not items_con_costo and items:
            import logging
            logging.warning(f"Hay {len(items)} items en la BD pero no se pudieron serializar. Retornando lista vacía.")
            # Retornar lista vacía en lugar de error para evitar 500
            return paginated_response([], skip=skip, limit=limit)
        
        return paginated_response(items_con_costo, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        import logging
        error_trace = traceback.format_exc()
        logging.error(f"Error crítico en listar_items: {str(e)}")
        logging.error(error_trace)
        # Asegurar rollback en caso de error
        try:
            if db.session.is_active:
                db.session.rollback()
        except Exception as rollback_error:
            logging.error(f"Error al hacer rollback: {str(rollback_error)}")
        
        # En lugar de retornar 500, retornar lista vacía para evitar que el frontend falle
        # El error ya está registrado en los logs para depuración
        logging.warning("Retornando lista vacía debido a error crítico (ver logs para detalles)")
        return paginated_response([], skip=0, limit=100)

@bp.route('/items', methods=['POST'])
@handle_db_transaction
def crear_item():
    """Crea un nuevo item."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    item = ItemService.crear_item(db.session, datos)
    db.session.commit()
    return success_response(item.to_dict(), 201, 'Item creado correctamente')

@bp.route('/items/<int:item_id>', methods=['GET'])
def obtener_item(item_id):
    """Obtiene un item por ID con costo promedio calculado."""
    try:
        validate_positive_int(item_id, 'item_id')
        item = ItemService.obtener_item(db.session, item_id)
        if not item:
            return error_response('Item no encontrado', 404, 'NOT_FOUND')
        
        item_dict = item.to_dict()
        costo_promedio = ItemService.calcular_costo_unitario_promedio(db.session, item_id)
        item_dict['costo_unitario_promedio'] = costo_promedio
        
        return success_response(item_dict)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/items/<int:item_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_item(item_id):
    """Actualiza un item existente."""
    validate_positive_int(item_id, 'item_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    item = ItemService.actualizar_item(db.session, item_id, datos)
    db.session.commit()
    return success_response(item.to_dict(), message='Item actualizado correctamente')

@bp.route('/items/<int:item_id>/costo', methods=['PUT'])
@handle_db_transaction
def actualizar_costo_item(item_id):
    """Actualiza el costo unitario de un item."""
    validate_positive_int(item_id, 'item_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    costo = require_field(datos, 'costo', float)
    if costo < 0:
        return error_response('El costo debe ser un número positivo', 400, 'VALIDATION_ERROR')
    
    item = ItemService.actualizar_costo_unitario(db.session, item_id, costo)
    db.session.commit()
    return success_response(item.to_dict(), message='Costo actualizado correctamente')

@bp.route('/items/<int:item_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_item(item_id):
    """Elimina un item (soft delete)."""
    validate_positive_int(item_id, 'item_id')
    
    ItemService.eliminar_item(db.session, item_id)
    db.session.commit()
    return success_response(None, message='Item eliminado correctamente')

@bp.route('/items/<int:item_id>/toggle-activo', methods=['PUT'])
@handle_db_transaction
def toggle_activo_item(item_id):
    """Activa o desactiva un item."""
    validate_positive_int(item_id, 'item_id')
    
    item = ItemService.toggle_activo(db.session, item_id)
    db.session.commit()
    estado = 'activado' if item.activo else 'desactivado'
    return success_response(item.to_dict(), message=f'Item {estado} correctamente')

# ========== RUTAS DE LABELS ==========

@bp.route('/labels', methods=['GET'])
def listar_labels():
    """Lista todas las labels disponibles."""
    import logging
    try:
        categoria = request.args.get('categoria_principal')
        activo = request.args.get('activo', 'true')
        
        # Verificar si hay labels, si no hay y no hay filtros específicos, generar datos mock
        total_labels = db.session.query(ItemLabel).count()
        if total_labels == 0 and not categoria:
            try:
                logging.info("No hay labels, generando datos mock...")
                from scripts.init_food_labels import init_food_labels
                init_food_labels()
            except Exception as mock_error:
                logging.warning(f"Error generando labels mock: {str(mock_error)}")
        
        query = db.session.query(ItemLabel)
        
        if categoria:
            query = query.filter(ItemLabel.categoria_principal == categoria)
        
        if activo.lower() == 'true':
            query = query.filter(ItemLabel.activo == True)
        
        labels = query.order_by(ItemLabel.categoria_principal, ItemLabel.nombre_es).all()
        return jsonify([l.to_dict() for l in labels]), 200
    except Exception as e:
        logging.error(f"Error en listar_labels: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@bp.route('/labels/categorias', methods=['GET'])
def listar_categorias_labels():
    """Lista las categorías principales de labels."""
    try:
        categorias = db.session.query(ItemLabel.categoria_principal).distinct().all()
        categorias_list = [cat[0] for cat in categorias]
        return jsonify(categorias_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/labels', methods=['POST'])
@handle_db_transaction
def crear_label():
    """Crea una nueva label/clasificación de alimentos."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Validar campos requeridos
    nombre_es = require_field(datos, 'nombre_es', str)
    categoria_principal = require_field(datos, 'categoria_principal', str)
    
    # Generar código si no se proporciona
    codigo = datos.get('codigo')
    if not codigo:
        # Generar código basado en categoría y nombre
        categoria_prefijo = categoria_principal[:3].upper().replace(' ', '_')
        nombre_prefijo = nombre_es[:5].upper().replace(' ', '_')
        codigo = f'{categoria_prefijo}_{nombre_prefijo}'
    
    # Verificar si ya existe una label con el mismo código
    existing = ItemLabel.query.filter_by(codigo=codigo).first()
    if existing:
        return error_response(f'Ya existe una clasificación con el código {codigo}', 400, 'DUPLICATE_ERROR')
    
    # Crear nueva label
    nueva_label = ItemLabel(
        codigo=codigo,
        nombre_es=nombre_es,
        nombre_en=datos.get('nombre_en', nombre_es),
        categoria_principal=categoria_principal,
        descripcion=datos.get('descripcion', ''),
        activo=datos.get('activo', True)
    )
    
    db.session.add(nueva_label)
    db.session.commit()
    
    return success_response(nueva_label.to_dict(), 201, 'Label creada correctamente')

# ========== RUTAS DE PEDIDOS AUTOMÁTICOS ==========

@bp.route('/pedidos/aprobar/<int:pedido_id>', methods=['POST'])
@handle_db_transaction
def aprobar_pedido(pedido_id):
    """Aprueba un pedido y programa el envío automático 1 hora después."""
    validate_positive_int(pedido_id, 'pedido_id')
    datos = request.get_json() or {}
    usuario_id = datos.get('usuario_id', 1)
    
    pedido = PedidosAutomaticosService.aprobar_y_programar_envio(
        db.session,
        pedido_id,
        usuario_id
    )
    db.session.commit()
    
    return success_response(
        pedido.to_dict(),
        message='Pedido aprobado. Se enviará automáticamente en 1 hora.'
    )

@bp.route('/pedidos/requerimientos-quincenales', methods=['GET'])
def calcular_requerimientos_quincenales():
    """Calcula requerimientos quincenales basados en programación."""
    try:
        from datetime import date
        
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_inicio = parse_date(fecha_inicio_str) if fecha_inicio_str else date.today()
        
        resultado = RequerimientosService.calcular_requerimientos_quincenales(
            db.session,
            fecha_inicio
        )
        
        # Convertir objetos a dicts
        requerimientos_dict = []
        for req in resultado['requerimientos']:
            req_dict = {
                'item_id': req['item_id'],
                'item': req['item'].to_dict() if req['item'] else None,
                'cantidad_necesaria': req['cantidad_necesaria'],
                'cantidad_actual': req['cantidad_actual'],
                'cantidad_minima': req['cantidad_minima'],
                'cantidad_a_pedir': req['cantidad_a_pedir'],
                'unidad': req['unidad'],
                'proveedor_id': req['proveedor_id'],
                'proveedor': req['proveedor'].to_dict() if req['proveedor'] else None
            }
            requerimientos_dict.append(req_dict)
        
        resultado['requerimientos'] = requerimientos_dict
        
        return success_response(resultado)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

# ========== RUTAS DE INVENTARIO ==========

@bp.route('/inventario', methods=['GET'])
def listar_inventario():
    """Lista el inventario completo o de un item específico."""
    import logging
    try:
        item_id = request.args.get('item_id', type=int)
        if item_id:
            validate_positive_int(item_id, 'item_id')
        
        inventario = InventarioService.obtener_inventario(db.session, item_id=item_id)
        
        # Si no hay inventario y no hay filtro específico, generar datos mock
        if not inventario and not item_id:
            try:
                logging.info("No hay inventario, generando datos mock...")
                from scripts.init_inventario import init_inventario
                init_inventario()
                # Volver a consultar después de crear los mock
                inventario = InventarioService.obtener_inventario(db.session, item_id=item_id)
            except Exception as mock_error:
                logging.warning(f"Error generando inventario mock: {str(mock_error)}")
        
        return success_response([inv.to_dict() for inv in inventario])
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        logging.error(f"Error en listar_inventario: {str(e)}", exc_info=True)
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/inventario/stock-bajo', methods=['GET'])
def obtener_stock_bajo():
    """Obtiene items con stock bajo."""
    import logging
    try:
        # Verificar si hay inventario, si no hay, generar datos mock
        from models.inventario import Inventario
        total_inventario = db.session.query(Inventario).count()
        if total_inventario == 0:
            try:
                logging.info("No hay inventario, generando datos mock...")
                from scripts.init_inventario import init_inventario
                init_inventario()
            except Exception as mock_error:
                logging.warning(f"Error generando inventario mock: {str(mock_error)}")
        
        items = InventarioService.obtener_stock_bajo(db.session)
        return success_response(items)
    except Exception as e:
        import traceback
        logging.error(f"Error en obtener_stock_bajo: {str(e)}")
        logging.error(traceback.format_exc())
        return success_response([])  # Retornar lista vacía en lugar de error

@bp.route('/inventario/<int:item_id>/verificar', methods=['POST'])
def verificar_disponibilidad(item_id):
    """Verifica disponibilidad de stock para un item."""
    try:
        validate_positive_int(item_id, 'item_id')
        datos = request.get_json()
        if not datos:
            return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
        
        cantidad_necesaria = require_field(datos, 'cantidad_necesaria', float)
        if cantidad_necesaria < 0:
            return error_response('La cantidad necesaria debe ser positiva', 400, 'VALIDATION_ERROR')
        
        disponibilidad = InventarioService.verificar_disponibilidad(
            db.session,
            item_id,
            cantidad_necesaria
        )
        
        return success_response(disponibilidad)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/inventario/completo', methods=['GET'])
def obtener_inventario_completo():
    """Obtiene inventario completo con últimos movimientos."""
    import logging
    import traceback
    try:
        # Verificar que la sesión esté activa
        try:
            if not db.session.is_active:
                db.session.rollback()
        except Exception as session_error:
            logging.warning(f"Error verificando sesión: {str(session_error)}")
            try:
                db.session.expire_all()
            except:
                pass
        
        inventario = InventarioService.obtener_inventario_completo_con_movimientos(db.session)
        
        # Asegurar que siempre retornamos una lista
        if not isinstance(inventario, list):
            logging.warning("obtener_inventario_completo_con_movimientos no retornó una lista, convirtiendo")
            inventario = []
        
        return success_response(inventario)
    except ValueError as e:
        logging.error(f"Error de validación en obtener_inventario_completo: {str(e)}")
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"Error en obtener_inventario_completo: {str(e)}")
        logging.error(error_trace)
        
        # Asegurar rollback en caso de error
        try:
            if db.session.is_active:
                db.session.rollback()
        except Exception as rollback_error:
            logging.error(f"Error al hacer rollback: {str(rollback_error)}")
        
        # Retornar lista vacía en lugar de error 500 para evitar que el frontend falle
        logging.warning("Retornando lista vacía debido a error (ver logs para detalles)")
        return success_response([])

@bp.route('/inventario/dashboard', methods=['GET'])
def obtener_dashboard_inventario():
    """Obtiene resumen tipo dashboard del inventario."""
    import logging
    try:
        # Verificar si hay inventario, si no hay, generar datos mock
        from models.inventario import Inventario
        total_inventario = db.session.query(Inventario).count()
        if total_inventario == 0:
            try:
                logging.info("No hay inventario, generando datos mock...")
                from scripts.init_inventario import init_inventario
                init_inventario()
            except Exception as mock_error:
                logging.warning(f"Error generando inventario mock: {str(mock_error)}")
        
        resumen = InventarioService.obtener_resumen_dashboard(db.session)
        
        # Asegurar estructura por defecto si hay error
        if not resumen or not isinstance(resumen, dict):
            resumen = {
                'total_items': 0,
                'items_bajo_stock': 0,
                'valor_total_inventario': 0.0,
                'items_por_categoria': {}
            }
        
        return success_response(resumen)
    except Exception as e:
        import traceback
        logging.error(f"Error en obtener_dashboard_inventario: {str(e)}")
        logging.error(traceback.format_exc())
        # Retornar estructura por defecto
        return success_response({
            'total_items': 0,
            'items_bajo_stock': 0,
            'valor_total_inventario': 0.0,
            'items_por_categoria': {}
        })

@bp.route('/inventario/silos', methods=['GET'])
def obtener_silos_inventario():
    """Obtiene los top 10 items más comprados para visualización tipo silos."""
    try:
        import logging
        import traceback
        
        # Verificar si hay facturas o pedidos, si no hay, generar datos mock
        total_facturas = db.session.query(Factura).count()
        from models.pedido import PedidoCompra
        total_pedidos = db.session.query(PedidoCompra).count()
        
        if total_facturas == 0 and total_pedidos == 0:
            try:
                logging.info("No hay datos de compras, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    from scripts.init_pedidos import init_pedidos
                    init_facturas(proveedores, items)
                    init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando datos de compras mock: {str(mock_error)}")
        
        # Verificar que la sesión esté activa
        try:
            if not db.session.is_active:
                db.session.rollback()
        except Exception as session_error:
            logging.warning(f"Error verificando sesión: {str(session_error)}")
            try:
                db.session.expire_all()
            except:
                pass
        
        silos = InventarioService.obtener_top_10_items_mas_comprados(db.session)
        
        # Asegurar que siempre retornamos una lista
        if not isinstance(silos, list):
            logging.warning("obtener_top_10_items_mas_comprados no retornó una lista, convirtiendo")
            silos = []
        
        return success_response(silos)
    except ValueError as e:
        import logging
        logging.error(f"Error de validación en obtener_silos_inventario: {str(e)}")
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import logging
        import traceback
        error_trace = traceback.format_exc()
        logging.error(f"Error en obtener_silos_inventario: {str(e)}")
        logging.error(error_trace)
        
        # Asegurar rollback en caso de error
        try:
            if db.session.is_active:
                db.session.rollback()
        except Exception as rollback_error:
            logging.error(f"Error al hacer rollback: {str(rollback_error)}")
        
        # Retornar lista vacía en lugar de error 500 para evitar que el frontend falle
        logging.warning("Retornando lista vacía debido a error (ver logs para detalles)")
        return success_response([])

# ========== RUTAS DE REQUERIMIENTOS ==========

@bp.route('/requerimientos', methods=['GET'])
def listar_requerimientos():
    """Lista requerimientos con filtros opcionales."""
    import logging
    try:
        estado = request.args.get('estado')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        # Verificar si hay requerimientos, si no hay y no hay filtros específicos, generar datos mock
        from models.requerimiento import Requerimiento
        total_requerimientos = db.session.query(Requerimiento).count()
        if total_requerimientos == 0 and not estado:
            try:
                logging.info("No hay requerimientos, generando datos mock...")
                from scripts.init_requerimientos import init_requerimientos
                init_requerimientos()
            except Exception as mock_error:
                logging.warning(f"Error generando requerimientos mock: {str(mock_error)}")
        
        requerimientos = RequerimientoService.listar_requerimientos(
            db.session,
            estado=estado,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([r.to_dict() for r in requerimientos], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        logging.error(f"Error en listar_requerimientos: {str(e)}", exc_info=True)
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/requerimientos', methods=['POST'])
@handle_db_transaction
def crear_requerimiento():
    """Crea un nuevo requerimiento."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    requerimiento = RequerimientoService.crear_requerimiento(db.session, datos)
    db.session.commit()
    return success_response(requerimiento.to_dict(), 201, 'Requerimiento creado correctamente')

@bp.route('/requerimientos/<int:requerimiento_id>/procesar', methods=['POST'])
@handle_db_transaction
def procesar_requerimiento(requerimiento_id):
    """Procesa un requerimiento entregando items y actualizando inventario."""
    validate_positive_int(requerimiento_id, 'requerimiento_id')
    requerimiento = RequerimientoService.procesar_requerimiento(
        db.session,
        requerimiento_id
    )
    db.session.commit()
    return success_response(requerimiento.to_dict(), message='Requerimiento procesado correctamente')

# ========== RUTAS DE FACTURAS ==========

@bp.route('/facturas', methods=['GET'])
def listar_facturas():
    """Lista facturas con filtros opcionales."""
    import logging
    try:
        proveedor_id = request.args.get('proveedor_id', type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        estado = request.args.get('estado')
        pendiente_confirmacion = request.args.get('pendiente_confirmacion', 'false').lower() == 'true'
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if proveedor_id:
            validate_positive_int(proveedor_id, 'proveedor_id')
        if cliente_id:
            validate_positive_int(cliente_id, 'cliente_id')
        
        # Verificar si hay facturas, si no hay y no hay filtros específicos, generar datos mock
        total_facturas = db.session.query(Factura).count()
        if total_facturas == 0 and not proveedor_id and not cliente_id and not estado:
            try:
                logging.info("No hay facturas, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    init_facturas(proveedores, items)
            except Exception as mock_error:
                logging.warning(f"Error generando facturas mock: {str(mock_error)}")
        
        query = db.session.query(Factura)
        
        if proveedor_id:
            query = query.filter(Factura.proveedor_id == proveedor_id)
        
        if cliente_id:
            query = query.filter(Factura.cliente_id == cliente_id)
        
        if estado:
            # Normalizar el estado: convertir a minúsculas y luego buscar en el enum
            estado_normalizado = estado.lower()
            # Mapear valores comunes a los valores del enum
            estado_map = {
                'pendiente': EstadoFactura.PENDIENTE,
                'parcial': EstadoFactura.PARCIAL,
                'aprobada': EstadoFactura.APROBADA,
                'rechazada': EstadoFactura.RECHAZADA
            }
            if estado_normalizado in estado_map:
                estado_enum = estado_map[estado_normalizado]
                # El TypeDecorator maneja la comparación automáticamente
                query = query.filter(Factura.estado == estado_enum)
            else:
                # Intentar con el valor directamente en mayúsculas
                try:
                    estado_enum = EstadoFactura[estado.upper()]
                    query = query.filter(Factura.estado == estado_enum)
                except KeyError:
                    return error_response(
                        f'Estado inválido: {estado}. Estados válidos: pendiente, parcial, aprobada, rechazada',
                        400,
                        'VALIDATION_ERROR'
                    )
        
        # Filtrar facturas pendientes de confirmación (con items sin cantidad_aprobada)
        if pendiente_confirmacion:
            # Usar exists y and_ que ya están importados al inicio del archivo
            query = query.filter(
                Factura.estado == EstadoFactura.PENDIENTE,
                exists().where(
                    and_(
                        FacturaItem.factura_id == Factura.id,
                        FacturaItem.cantidad_aprobada.is_(None)
                    )
                )
            )
        
        facturas = query.order_by(Factura.fecha_recepcion.desc()).offset(skip).limit(limit).all()
        
        # Serializar facturas con manejo de errores
        facturas_dict = []
        for f in facturas:
            try:
                facturas_dict.append(f.to_dict())
            except Exception as e:
                import logging
                logging.error(f"Error serializando factura {f.id}: {str(e)}")
                # Continuar con la siguiente factura
                continue
        
        return paginated_response(facturas_dict, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error en listar_facturas: {str(e)}")
        logging.error(traceback.format_exc())
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/facturas/ultima', methods=['GET'])
def obtener_ultima_factura():
    """Obtiene la última factura ingresada."""
    import logging
    try:
        # Verificar si hay facturas, si no hay, generar datos mock
        total_facturas = db.session.query(Factura).count()
        if total_facturas == 0:
            try:
                logging.info("No hay facturas, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    init_facturas(proveedores, items)
            except Exception as mock_error:
                logging.warning(f"Error generando facturas mock: {str(mock_error)}")
        
        factura = db.session.query(Factura).order_by(Factura.fecha_recepcion.desc()).first()
        if not factura:
            return success_response(None)  # Retornar null en lugar de error 404
        try:
            factura_dict = factura.to_dict()
            return success_response(factura_dict)
        except Exception as e:
            import logging
            import traceback
            logging.error(f"Error serializando factura {factura.id}: {str(e)}")
            logging.error(traceback.format_exc())
            # Retornar datos básicos si hay error en to_dict()
            try:
                return success_response({
                    'id': factura.id,
                    'numero_factura': factura.numero_factura,
                    'estado': factura.estado.value if factura.estado else None,
                    'warning': 'Error al serializar datos completos'
                })
            except Exception as e2:
                return error_response(f'Error al obtener factura: {str(e2)}', 500, 'INTERNAL_ERROR')
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error en obtener_ultima_factura: {str(e)}")
        logging.error(traceback.format_exc())
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/facturas/ingresar-imagen', methods=['POST'])
@handle_db_transaction
def ingresar_factura_imagen():
    """Ingresa una factura desde una imagen usando OCR."""
    if 'imagen' not in request.files:
        return error_response('No se proporcionó imagen', 400, 'VALIDATION_ERROR')
    
    archivo = request.files['imagen']
    tipo = request.form.get('tipo', 'proveedor')
    
    if tipo not in ('proveedor', 'cliente'):
        return error_response('Tipo inválido. Use "proveedor" o "cliente"', 400, 'VALIDATION_ERROR')
    
    # Validar y guardar archivo
    try:
        filename, temp_path = validate_file_upload(archivo)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    
    try:
        # Procesar factura
        factura = FacturaService.procesar_factura_desde_imagen(
            db.session,
            temp_path,
            tipo=tipo
        )
        db.session.commit()
        
        return success_response(factura.to_dict(), 201, 'Factura procesada correctamente')
    finally:
        # Eliminar archivo temporal
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass  # Ignorar errores al eliminar archivo temporal

@bp.route('/facturas/<int:factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    """Obtiene una factura por ID."""
    try:
        validate_positive_int(factura_id, 'factura_id')
        factura = db.session.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            return error_response('Factura no encontrada', 404, 'NOT_FOUND')
        return success_response(factura.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/facturas/<int:factura_id>/aprobar', methods=['POST'])
@handle_db_transaction
def aprobar_factura(factura_id):
    """Aprueba una factura y actualiza inventario."""
    validate_positive_int(factura_id, 'factura_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    items_aprobados = datos.get('items_aprobados', [])
    usuario_id = require_field(datos, 'usuario_id', int)
    aprobar_parcial = datos.get('aprobar_parcial', False)
    observaciones = datos.get('observaciones')
    
    factura = FacturaService.aprobar_factura(
        db.session,
        factura_id,
        items_aprobados,
        usuario_id,
        aprobar_parcial,
        observaciones
    )
    db.session.commit()
    
    return success_response(factura.to_dict(), message='Factura aprobada correctamente')

@bp.route('/facturas/<int:factura_id>/rechazar', methods=['POST'])
@handle_db_transaction
def rechazar_factura(factura_id):
    """Rechaza una factura."""
    validate_positive_int(factura_id, 'factura_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    usuario_id = require_field(datos, 'usuario_id', int)
    motivo = datos.get('motivo', 'Factura rechazada')
    
    factura = FacturaService.rechazar_factura(
        db.session,
        factura_id,
        usuario_id,
        motivo
    )
    db.session.commit()
    
    return success_response(factura.to_dict(), message='Factura rechazada correctamente')

@bp.route('/facturas/<int:factura_id>/revision', methods=['POST'])
@handle_db_transaction
def enviar_a_revision(factura_id):
    """Envía una factura a revisión."""
    validate_positive_int(factura_id, 'factura_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    usuario_id = require_field(datos, 'usuario_id', int)
    observaciones = datos.get('observaciones', '')
    
    factura = FacturaService.enviar_a_revision(
        db.session,
        factura_id,
        usuario_id,
        observaciones
    )
    db.session.commit()
    
    return success_response(factura.to_dict(), message='Factura enviada a revisión correctamente')

# ========== RUTAS DE PEDIDOS ==========

@bp.route('/pedidos', methods=['GET'])
def listar_pedidos():
    """Lista pedidos con filtros opcionales."""
    import logging
    try:
        proveedor_id = request.args.get('proveedor_id', type=int)
        estado = request.args.get('estado')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if proveedor_id:
            validate_positive_int(proveedor_id, 'proveedor_id')
        
        # Verificar si hay pedidos, si no hay y no hay filtros específicos, generar datos mock
        from models.pedido import PedidoCompra
        total_pedidos = db.session.query(PedidoCompra).count()
        if total_pedidos == 0 and not proveedor_id and not estado:
            try:
                logging.info("No hay pedidos, generando datos mock...")
                from scripts.init_pedidos import init_pedidos
                init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando pedidos mock: {str(mock_error)}")
        
        pedidos = PedidoCompraService.listar_pedidos(
            db.session,
            proveedor_id=proveedor_id,
            estado=estado,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([p.to_dict() for p in pedidos], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/pedidos', methods=['POST'])
@handle_db_transaction
def crear_pedido():
    """Crea un nuevo pedido de compra."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    pedido = PedidoCompraService.crear_pedido(db.session, datos)
    db.session.commit()
    return success_response(pedido.to_dict(), 201, 'Pedido creado correctamente')

@bp.route('/pedidos/automatico', methods=['POST'])
@handle_db_transaction
def generar_pedido_automatico():
    """Genera pedidos automáticos agrupados por proveedor."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    items_necesarios = datos.get('items_necesarios', [])
    usuario_id = require_field(datos, 'usuario_id', int)
    
    pedidos = PedidoCompraService.generar_pedido_automatico(
        db.session,
        items_necesarios,
        usuario_id
    )
    db.session.commit()
    
    return success_response([p.to_dict() for p in pedidos], 201, f'{len(pedidos)} pedidos generados correctamente')

@bp.route('/pedidos/<int:pedido_id>/enviar', methods=['POST'])
@handle_db_transaction
def enviar_pedido(pedido_id):
    """Envía un pedido al proveedor."""
    validate_positive_int(pedido_id, 'pedido_id')
    pedido = PedidoCompraService.enviar_pedido(db.session, pedido_id)
    db.session.commit()
    return success_response(pedido.to_dict(), message='Pedido enviado correctamente')

# ========== RUTAS DE ESTADÍSTICAS DE COMPRAS ==========

@bp.route('/compras/resumen', methods=['GET'])
def resumen_compras():
    """Obtiene resumen general de compras."""
    import logging
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay datos de compras (facturas o pedidos)
        total_facturas = db.session.query(Factura).count()
        from models.pedido import PedidoCompra
        total_pedidos = db.session.query(PedidoCompra).count()
        
        if total_facturas == 0 and total_pedidos == 0:
            try:
                logging.info("No hay datos de compras, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    from scripts.init_pedidos import init_pedidos
                    init_facturas(proveedores, items)
                    init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando datos de compras mock: {str(mock_error)}")
        
        resumen = ComprasStatsService.obtener_resumen_general(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj
        )
        
        # Asegurar que siempre retornamos la estructura correcta
        if not resumen or 'resumen' not in resumen:
            # Si no hay resumen, crear uno por defecto
            from datetime import date, timedelta
            fecha_desde_default = fecha_desde_obj or (date.today() - timedelta(days=30))
            fecha_hasta_default = fecha_hasta_obj or date.today()
            resumen = {
                'periodo': {
                    'fecha_desde': fecha_desde_default.isoformat(),
                    'fecha_hasta': fecha_hasta_default.isoformat()
                },
                'resumen': {
                    'total_pedidos': 0,
                    'total_facturas': 0,
                    'total_gastado': 0.0,
                    'total_gastado_pedidos': 0.0,
                    'total_gastado_facturas': 0.0,
                    'pedidos_pendientes': 0
                },
                'pedidos_por_estado': {}
            }
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import logging
        import traceback
        logging.error(f"Error en resumen_compras: {str(e)}")
        logging.error(traceback.format_exc())
        # Retornar estructura por defecto en caso de error
        from datetime import date, timedelta
        fecha_desde_default = date.today() - timedelta(days=30)
        fecha_hasta_default = date.today()
        resumen_default = {
            'periodo': {
                'fecha_desde': fecha_desde_default.isoformat(),
                'fecha_hasta': fecha_hasta_default.isoformat()
            },
            'resumen': {
                'total_pedidos': 0,
                'total_facturas': 0,
                'total_gastado': 0.0,
                'total_gastado_pedidos': 0.0,
                'total_gastado_facturas': 0.0,
                'pedidos_pendientes': 0
            },
            'pedidos_por_estado': {}
        }
        return success_response(resumen_default)

@bp.route('/compras/por-item', methods=['GET'])
def compras_por_item():
    """Obtiene resumen de compras agrupado por item."""
    import logging
    import traceback
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = validate_positive_int(request.args.get('limite', 20), 'limite')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay datos antes de procesar
        total_pedidos = db.session.query(PedidoCompra).count()
        total_facturas = db.session.query(Factura).count()
        
        if total_pedidos == 0 and total_facturas == 0:
            # Generar datos mock si no hay datos
            try:
                logging.info("No hay datos de compras, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    from scripts.init_pedidos import init_pedidos
                    init_facturas(proveedores, items)
                    init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando datos de compras mock: {str(mock_error)}")
        
        resumen = ComprasStatsService.obtener_resumen_por_item(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            limite=limite
        )
        
        # Asegurar que siempre retornamos una lista
        if not isinstance(resumen, list):
            resumen = []
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        logging.error(f"Error en compras_por_item: {str(e)}")
        logging.error(traceback.format_exc())
        # Retornar lista vacía en caso de error
        return success_response([])

@bp.route('/compras/por-proveedor', methods=['GET'])
def compras_por_proveedor():
    """Obtiene resumen de compras agrupado por proveedor."""
    import logging
    import traceback
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = validate_positive_int(request.args.get('limite', 20), 'limite')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay datos antes de procesar
        total_pedidos = db.session.query(PedidoCompra).count()
        total_facturas = db.session.query(Factura).count()
        
        if total_pedidos == 0 and total_facturas == 0:
            # Generar datos mock si no hay datos
            try:
                logging.info("No hay datos de compras, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    from scripts.init_pedidos import init_pedidos
                    init_facturas(proveedores, items)
                    init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando datos de compras mock: {str(mock_error)}")
        
        resumen = ComprasStatsService.obtener_resumen_por_proveedor(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            limite=limite
        )
        
        # Asegurar que siempre retornamos una lista
        if not isinstance(resumen, list):
            resumen = []
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        logging.error(f"Error en compras_por_proveedor: {str(e)}")
        logging.error(traceback.format_exc())
        # Retornar lista vacía en caso de error
        return success_response([])

@bp.route('/compras/por-proceso', methods=['GET'])
def compras_por_proceso():
    """Obtiene estadísticas de compras relacionadas con procesos de inventario y programación."""
    import logging
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay datos antes de procesar
        total_pedidos = db.session.query(PedidoCompra).count()
        total_facturas = db.session.query(Factura).count()
        
        if total_pedidos == 0 and total_facturas == 0:
            # Generar datos mock si no hay datos
            try:
                logging.info("No hay datos de compras, generando datos mock...")
                proveedores = db.session.query(Proveedor).all()
                items = db.session.query(Item).filter(Item.activo == True).all()
                if proveedores and items:
                    from scripts.init_facturas import init_facturas
                    from scripts.init_pedidos import init_pedidos
                    init_facturas(proveedores, items)
                    init_pedidos()
            except Exception as mock_error:
                logging.warning(f"Error generando datos de compras mock: {str(mock_error)}")
        
        resumen = ComprasStatsService.obtener_compras_por_proceso(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj
        )
        
        # Asegurar estructura por defecto si hay error
        if not resumen or not isinstance(resumen, dict):
            resumen = {
                'pedidos_automaticos': {'cantidad': 0, 'total_gastado': 0.0},
                'programaciones': {'cantidad': 0},
                'inventario': {'items_bajo_stock': 0, 'total_items': 0, 'porcentaje_bajo_stock': 0}
            }
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        logging.error(f"Error en compras_por_proceso: {str(e)}")
        logging.error(traceback.format_exc())
        # Retornar estructura por defecto
        return success_response({
            'pedidos_automaticos': {'cantidad': 0, 'total_gastado': 0.0},
            'programaciones': {'cantidad': 0},
            'inventario': {'items_bajo_stock': 0, 'total_items': 0, 'porcentaje_bajo_stock': 0}
        })

# ========== RUTAS DE COSTOS ESTANDARIZADOS ==========

@bp.route('/costos', methods=['GET'])
def listar_costos():
    """Lista costos estandarizados con filtros opcionales."""
    import logging
    try:
        label_id = request.args.get('label_id', type=int)
        categoria = request.args.get('categoria')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if label_id:
            validate_positive_int(label_id, 'label_id')
        
        # Verificar si hay costos, si no hay y no hay filtros específicos, generar datos mock
        from models.costo_item import CostoItem
        total_costos = db.session.query(CostoItem).count()
        if total_costos == 0 and not label_id and not categoria:
            try:
                logging.info("No hay costos, generando datos mock...")
                # Primero asegurar que hay facturas aprobadas para calcular costos
                total_facturas = db.session.query(Factura).count()
                if total_facturas == 0:
                    proveedores = db.session.query(Proveedor).all()
                    items = db.session.query(Item).filter(Item.activo == True).all()
                    if proveedores and items:
                        from scripts.init_facturas import init_facturas
                        init_facturas(proveedores, items)
                # Generar costos
                from scripts.init_costos import init_costos
                init_costos()
            except Exception as mock_error:
                logging.warning(f"Error generando costos mock: {str(mock_error)}")
        
        costos = CostoService.listar_costos_estandarizados(
            db.session,
            label_id=label_id,
            categoria=categoria,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([c.to_dict() for c in costos], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        logging.error(f"Error en listar_costos: {str(e)}")
        logging.error(traceback.format_exc())
        return paginated_response([], skip=skip, limit=limit)

@bp.route('/costos/<int:item_id>', methods=['GET'])
def obtener_costo_item(item_id):
    """Obtiene el costo estandarizado de un item específico."""
    import logging
    try:
        validate_positive_int(item_id, 'item_id')
        
        # Verificar si existe el costo, si no existe, intentar calcularlo
        from models.costo_item import CostoItem
        costo = db.session.query(CostoItem).filter(
            CostoItem.item_id == item_id
        ).first()
        
        if not costo:
            # Intentar calcular el costo si hay facturas aprobadas
            try:
                logging.info(f"No hay costo para item {item_id}, intentando calcular...")
                # Verificar si hay facturas aprobadas
                total_facturas = db.session.query(Factura).filter(
                    Factura.estado == EstadoFactura.APROBADA
                ).count()
                
                if total_facturas == 0:
                    # Generar facturas mock primero
                    proveedores = db.session.query(Proveedor).all()
                    items = db.session.query(Item).filter(Item.activo == True).all()
                    if proveedores and items:
                        from scripts.init_facturas import init_facturas
                        init_facturas(proveedores, items)
                
                # Intentar calcular el costo
                costo = CostoService.calcular_y_almacenar_costo_estandarizado(db.session, item_id)
                if costo:
                    db.session.commit()
            except Exception as calc_error:
                logging.warning(f"Error calculando costo para item {item_id}: {str(calc_error)}")
        
        if not costo:
            return error_response('Costo no encontrado para este item', 404, 'NOT_FOUND')
        return success_response(costo.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        logging.error(f"Error en obtener_costo_item: {str(e)}")
        logging.error(traceback.format_exc())
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/costos/<int:item_id>/calcular', methods=['POST'])
@handle_db_transaction
def calcular_costo_item(item_id):
    """Calcula y almacena el costo estandarizado de un item."""
    validate_positive_int(item_id, 'item_id')
    costo = CostoService.calcular_y_almacenar_costo_estandarizado(db.session, item_id)
    if not costo:
        return error_response('No hay suficientes facturas aprobadas para calcular el costo', 404, 'NOT_FOUND')
    db.session.commit()
    return success_response(costo.to_dict(), message='Costo calculado correctamente')

@bp.route('/costos/recalcular-todos', methods=['POST'])
@handle_db_transaction
def recalcular_todos_costos():
    """Recalcula todos los costos estandarizados de items y recetas."""
    estadisticas = CostoService.recalcular_todos_los_costos(db.session)
    db.session.commit()
    return success_response(estadisticas, message='Recálculo completado')

@bp.route('/costos/recetas', methods=['GET'])
@handle_db_transaction
def listar_costos_recetas():
    """Lista costos de recetas con filtros opcionales."""
    try:
        tipo = request.args.get('tipo')
        activa = request.args.get('activa')
        busqueda = request.args.get('busqueda')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        query = db.session.query(Receta)
        
        if activa is not None:
            activa_bool = activa.lower() == 'true'
            query = query.filter(Receta.activa == activa_bool)
        else:
            query = query.filter(Receta.activa == True)
        
        if tipo:
            try:
                tipo_enum = TipoReceta[tipo.upper()]
                query = query.filter(Receta.tipo == tipo_enum)
            except KeyError:
                pass
        
        if busqueda:
            query = query.filter(Receta.nombre.ilike(f'%{busqueda}%'))
        
        # Agregar eager loading para ingredientes e items relacionados
        from sqlalchemy.orm import selectinload, joinedload
        query = query.options(
            selectinload(Receta.ingredientes).joinedload('item')
        )
        
        recetas = query.order_by(Receta.nombre).offset(skip).limit(limit).all()
        
        # Recalcular costos antes de retornar (por si acaso)
        for receta in recetas:
            try:
                receta.calcular_totales()
            except Exception as e:
                import logging
                logging.warning(f"Error calculando totales de receta {receta.id}: {str(e)}")
        
        db.session.commit()
        
        resultado = []
        for receta in recetas:
            try:
                receta_dict = receta.to_dict()
                
                # Contar ingredientes con costo
                ingredientes_con_costo = 0
                total_ingredientes = 0
                if receta.ingredientes:
                    for ing in receta.ingredientes:
                        total_ingredientes += 1
                        if ing.item and ing.item.costo_unitario_actual:
                            ingredientes_con_costo += 1
                
                # Agregar información adicional de costos
                receta_dict['costo_info'] = {
                    'costo_total': float(receta.costo_total) if receta.costo_total else None,
                    'costo_por_porcion': float(receta.costo_por_porcion) if receta.costo_por_porcion else None,
                    'porciones': receta.porciones,
                    'porcion_gramos': float(receta.porcion_gramos) if receta.porcion_gramos else None,
                    'ingredientes_con_costo': ingredientes_con_costo,
                    'total_ingredientes': total_ingredientes
                }
                resultado.append(receta_dict)
            except Exception as e:
                import logging
                logging.error(f"Error procesando receta {receta.id} en costos/recetas: {str(e)}", exc_info=True)
                # Continuar con las demás recetas aunque una falle
                continue
        
        return paginated_response(resultado, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

# ========== RUTAS DE PEDIDOS INTERNOS (BODEGA → COCINA) ==========

@bp.route('/pedidos-internos', methods=['GET'])
def listar_pedidos_internos():
    """Lista pedidos internos con filtros opcionales."""
    import logging
    try:
        estado = request.args.get('estado')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        fecha_desde_dt = parse_datetime(fecha_desde) if fecha_desde else None
        fecha_hasta_dt = parse_datetime(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay pedidos internos, si no hay y no hay filtros específicos, generar datos mock
        from models.pedido_interno import PedidoInterno
        total_pedidos_internos = db.session.query(PedidoInterno).count()
        if total_pedidos_internos == 0 and not estado and not fecha_desde and not fecha_hasta:
            try:
                logging.info("No hay pedidos internos, generando datos mock...")
                from scripts.init_pedidos_internos import init_pedidos_internos
                init_pedidos_internos()
            except Exception as mock_error:
                logging.warning(f"Error generando pedidos internos mock: {str(mock_error)}")
        
        pedidos = PedidoInternoService.listar_pedidos_internos(
            db.session,
            estado=estado,
            fecha_desde=fecha_desde_dt,
            fecha_hasta=fecha_hasta_dt,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([p.to_dict() for p in pedidos], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        logging.error(f"Error en listar_pedidos_internos: {str(e)}", exc_info=True)
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/pedidos-internos', methods=['POST'])
@handle_db_transaction
def crear_pedido_interno():
    """Crea un nuevo pedido interno."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    pedido = PedidoInternoService.crear_pedido_interno(db.session, datos)
    db.session.commit()
    return success_response(pedido.to_dict(), 201, 'Pedido interno creado correctamente')

@bp.route('/pedidos-internos/<int:pedido_id>', methods=['GET'])
def obtener_pedido_interno(pedido_id):
    """Obtiene un pedido interno por ID."""
    try:
        validate_positive_int(pedido_id, 'pedido_id')
        pedido = PedidoInternoService.obtener_pedido_interno(db.session, pedido_id)
        if not pedido:
            return error_response('Pedido interno no encontrado', 404, 'NOT_FOUND')
        return success_response(pedido.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/pedidos-internos/<int:pedido_id>/confirmar', methods=['POST'])
@handle_db_transaction
def confirmar_entrega_pedido_interno(pedido_id):
    """Confirma la entrega de un pedido interno y actualiza el inventario."""
    validate_positive_int(pedido_id, 'pedido_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    recibido_por_id = require_field(datos, 'recibido_por_id', int)
    recibido_por_nombre = require_field(datos, 'recibido_por_nombre', str)
    
    pedido = PedidoInternoService.confirmar_entrega(
        db.session,
        pedido_id,
        recibido_por_id,
        recibido_por_nombre
    )
    db.session.commit()
    return success_response(pedido.to_dict(), message='Entrega confirmada correctamente')

@bp.route('/pedidos-internos/<int:pedido_id>/cancelar', methods=['POST'])
@handle_db_transaction
def cancelar_pedido_interno(pedido_id):
    """Cancela un pedido interno pendiente."""
    validate_positive_int(pedido_id, 'pedido_id')
    pedido = PedidoInternoService.cancelar_pedido(db.session, pedido_id)
    db.session.commit()
    return success_response(pedido.to_dict(), message='Pedido cancelado correctamente')
