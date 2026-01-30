"""
Rutas API para módulo de Planificación.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
from models.programacion import ProgramacionMenu, ProgramacionMenuItem
from modules.planificacion.recetas import RecetaService
from modules.planificacion.programacion import ProgramacionMenuService
from modules.crm.tickets_automaticos import TicketsAutomaticosService
from modules.logistica.pedidos_automaticos import PedidosAutomaticosService
from utils.route_helpers import (
    handle_db_transaction, parse_date, require_field,
    validate_positive_int, success_response,
    error_response, paginated_response
)

bp = Blueprint('planificacion', __name__)

# ========== RUTAS DE RECETAS ==========

@bp.route('/recetas', methods=['GET'])
def listar_recetas():
    """Lista recetas con filtros opcionales."""
    try:
        activa = request.args.get('activa')
        tipo = request.args.get('tipo')
        busqueda = request.args.get('busqueda')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        activa_bool = None if activa is None else activa.lower() == 'true'
        
        recetas = RecetaService.listar_recetas(
            db.session,
            activa=activa_bool,
            tipo=tipo,
            busqueda=busqueda,
            skip=skip,
            limit=limit
        )
        
        # Convertir recetas a diccionarios con manejo de errores robusto
        recetas_dict = []
        for receta in recetas:
            try:
                # Asegurar que la sesión esté activa antes de convertir
                if not db.session.is_active:
                    try:
                        db.session.rollback()
                    except:
                        pass
                
                # Forzar carga de ingredientes si es necesario (evitar lazy loading)
                try:
                    _ = receta.ingredientes  # Forzar carga si es necesario
                    # Si ingredientes es una relación lazy, convertirlo a lista
                    if hasattr(receta.ingredientes, '__iter__') and not isinstance(receta.ingredientes, list):
                        try:
                            _ = list(receta.ingredientes)
                        except:
                            pass
                except Exception:
                    pass  # Si falla, continuar sin ingredientes
                
                receta_dict = receta.to_dict()
                recetas_dict.append(receta_dict)
            except Exception as e:
                import logging
                import traceback
                logging.error(f"Error al convertir receta {receta.id if hasattr(receta, 'id') else 'N/A'} a dict: {str(e)}", exc_info=True)
                logging.debug(traceback.format_exc())
                
                # Agregar receta básica sin ingredientes si falla la conversión completa
                try:
                    # Manejar tipo de manera segura
                    tipo_value = None
                    try:
                        if hasattr(receta, 'tipo') and receta.tipo:
                            if isinstance(receta.tipo, str):
                                tipo_value = receta.tipo.lower()
                            elif hasattr(receta.tipo, 'value'):
                                tipo_value = receta.tipo.value
                            else:
                                tipo_value = str(receta.tipo).lower()
                    except:
                        tipo_value = 'almuerzo'  # Valor por defecto
                    
                    recetas_dict.append({
                        'id': receta.id if hasattr(receta, 'id') else None,
                        'nombre': receta.nombre if hasattr(receta, 'nombre') else 'Error',
                        'tipo': tipo_value or 'almuerzo',
                        'activa': receta.activa if hasattr(receta, 'activa') else False,
                        'ingredientes': [],
                        'error': f'Error al cargar: {str(e)}'
                    })
                except Exception as e2:
                    logging.error(f"Error crítico serializando receta básica: {str(e2)}")
                    # Continuar sin agregar esta receta
                    continue
        
        return paginated_response(recetas_dict, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import logging
        import traceback
        error_trace = traceback.format_exc()
        logging.error(f"Error en listar_recetas: {str(e)}\n{error_trace}", exc_info=True)
        # Asegurar rollback en caso de error
        try:
            db.session.rollback()
        except:
            pass
        return error_response(f"Error al listar recetas: {str(e)}", 500, 'INTERNAL_ERROR')

@bp.route('/recetas', methods=['POST'])
@handle_db_transaction
def crear_receta():
    """Crea una nueva receta."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    receta = RecetaService.crear_receta(db.session, datos)
    db.session.commit()
    return success_response(receta.to_dict(), 201, 'Receta creada correctamente')

@bp.route('/recetas/<int:receta_id>', methods=['GET'])
def obtener_receta(receta_id):
    """Obtiene una receta por ID."""
    try:
        validate_positive_int(receta_id, 'receta_id')
        receta = RecetaService.obtener_receta(db.session, receta_id)
        if not receta:
            return error_response('Receta no encontrada', 404, 'NOT_FOUND')
        return success_response(receta.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/recetas/<int:receta_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_receta(receta_id):
    """Actualiza una receta existente."""
    validate_positive_int(receta_id, 'receta_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    receta = RecetaService.actualizar_receta(db.session, receta_id, datos)
    db.session.commit()
    return success_response(receta.to_dict(), message='Receta actualizada correctamente')

@bp.route('/recetas/<int:receta_id>/duplicar', methods=['POST'])
@handle_db_transaction
def duplicar_receta(receta_id):
    """Duplica una receta existente."""
    validate_positive_int(receta_id, 'receta_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    nuevo_nombre = require_field(datos, 'nuevo_nombre', str)
    
    receta = RecetaService.duplicar_receta(db.session, receta_id, nuevo_nombre)
    db.session.commit()
    return success_response(receta.to_dict(), 201, 'Receta duplicada correctamente')

@bp.route('/recetas/<int:receta_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_receta(receta_id):
    """Elimina una receta."""
    try:
        validate_positive_int(receta_id, 'receta_id')
        RecetaService.eliminar_receta(db.session, receta_id)
        db.session.commit()
        return success_response(None, message='Receta eliminada correctamente')
    except ValueError as e:
        return error_response(str(e), 404, 'NOT_FOUND')
    except Exception as e:
        import logging
        logging.error(f"Error al eliminar receta {receta_id}: {str(e)}", exc_info=True)
        return error_response(f"Error al eliminar receta: {str(e)}", 500, 'INTERNAL_ERROR')

@bp.route('/recetas/<int:receta_id>/activar', methods=['PATCH'])
@handle_db_transaction
def activar_desactivar_receta(receta_id):
    """Activa o desactiva una receta."""
    try:
        validate_positive_int(receta_id, 'receta_id')
        datos = request.get_json() or {}
        activa = datos.get('activa', True)
        
        receta = RecetaService.activar_desactivar_receta(db.session, receta_id, activa)
        db.session.commit()
        return success_response(receta.to_dict(), message=f'Receta {"activada" if activa else "desactivada"} correctamente')
    except ValueError as e:
        return error_response(str(e), 404, 'NOT_FOUND')
    except Exception as e:
        import logging
        logging.error(f"Error al activar/desactivar receta {receta_id}: {str(e)}", exc_info=True)
        return error_response(f"Error al activar/desactivar receta: {str(e)}", 500, 'INTERNAL_ERROR')

# ========== RUTAS DE PROGRAMACIÓN ==========

@bp.route('/programacion', methods=['GET'])
def listar_programaciones():
    """Lista programaciones con filtros opcionales."""
    import logging
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        ubicacion = request.args.get('ubicacion')
        tiempo_comida = request.args.get('tiempo_comida')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        # Verificar si hay programaciones, si no hay y no hay filtros específicos, generar datos mock
        total_programaciones = db.session.query(ProgramacionMenu).count()
        if total_programaciones == 0 and not fecha_desde and not fecha_hasta and not ubicacion and not tiempo_comida:
            try:
                logging.info("No hay programaciones, generando datos mock...")
                # Verificar que haya recetas
                from models.receta import Receta
                total_recetas = db.session.query(Receta).filter(Receta.activa == True).count()
                if total_recetas == 0:
                    # Generar recetas primero
                    from scripts.init_recetas import init_recetas
                    init_recetas()
                
                # Generar programaciones
                from scripts.init_programacion import init_programacion
                init_programacion()
            except Exception as mock_error:
                logging.warning(f"Error generando programaciones mock: {str(mock_error)}")
        
        programaciones = ProgramacionMenuService.listar_programaciones(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            ubicacion=ubicacion,
            tiempo_comida=tiempo_comida,
            skip=skip,
            limit=limit
        )
        
        # Convertir programaciones a diccionarios con manejo de errores robusto
        programaciones_dict = []
        for p in programaciones:
            try:
                programaciones_dict.append(p.to_dict())
            except Exception as e:
                import logging
                logging.error(f"Error al convertir programación {p.id if hasattr(p, 'id') else 'N/A'} a dict: {str(e)}", exc_info=True)
                # Agregar programación básica si falla la conversión completa
                try:
                    programaciones_dict.append({
                        'id': p.id if hasattr(p, 'id') else None,
                        'fecha': p.fecha.isoformat() if hasattr(p, 'fecha') and p.fecha else None,
                        'fecha_desde': p.fecha.isoformat() if hasattr(p, 'fecha') and p.fecha else None,
                        'fecha_hasta': p.fecha.isoformat() if hasattr(p, 'fecha') and p.fecha else None,
                        'tiempo_comida': p.tiempo_comida.value if hasattr(p, 'tiempo_comida') and p.tiempo_comida else None,
                        'ubicacion': p.ubicacion if hasattr(p, 'ubicacion') else None,
                        'items': [],
                        'error': f'Error al cargar: {str(e)}'
                    })
                except:
                    # Si incluso esto falla, continuar sin agregar esta programación
                    continue
        
        return paginated_response(programaciones_dict, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import logging
        import traceback
        error_trace = traceback.format_exc()
        logging.error(f"Error en listar_programaciones: {str(e)}\n{error_trace}", exc_info=True)
        return error_response(f"Error al listar programaciones: {str(e)}", 500, 'INTERNAL_ERROR')

@bp.route('/programacion', methods=['POST'])
@handle_db_transaction
def crear_programacion():
    """Crea una nueva programación de menú y genera pedidos automáticamente."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Convertir fechas string a date
    # Si viene 'fecha', usar para ambas fechas
    if 'fecha' in datos and isinstance(datos['fecha'], str):
        fecha = parse_date(datos['fecha'])
        if 'fecha_desde' not in datos or not datos['fecha_desde']:
            datos['fecha_desde'] = fecha
        if 'fecha_hasta' not in datos or not datos['fecha_hasta']:
            datos['fecha_hasta'] = fecha
    
    # Convertir fecha_desde y fecha_hasta si vienen como strings
    if 'fecha_desde' in datos and isinstance(datos['fecha_desde'], str):
        datos['fecha_desde'] = parse_date(datos['fecha_desde'])
    
    if 'fecha_hasta' in datos and isinstance(datos['fecha_hasta'], str):
        datos['fecha_hasta'] = parse_date(datos['fecha_hasta'])
    
    # Validar que fecha_hasta >= fecha_desde
    if datos.get('fecha_desde') and datos.get('fecha_hasta'):
        if datos['fecha_hasta'] < datos['fecha_desde']:
            return error_response('fecha_hasta debe ser mayor o igual a fecha_desde', 400, 'VALIDATION_ERROR')
    
    # Asegurar que 'fecha' tenga un valor (usar fecha_desde como fallback)
    # Esto es necesario porque la columna 'fecha' tiene NOT NULL en la BD
    if 'fecha' not in datos or datos['fecha'] is None:
        if datos.get('fecha_desde'):
            # Asegurar que fecha_desde esté convertido a date si viene como string
            if isinstance(datos['fecha_desde'], str):
                datos['fecha'] = parse_date(datos['fecha_desde'])
            else:
                datos['fecha'] = datos['fecha_desde']
        else:
            return error_response('Se requiere fecha_desde o fecha para crear la programación', 400, 'VALIDATION_ERROR')
    elif isinstance(datos['fecha'], str):
        # Si fecha viene como string, convertirla a date
        datos['fecha'] = parse_date(datos['fecha'])
    
    # Convertir tiempo_comida string a nombre del enum (mayúsculas) si viene como string
    # PostgreSQL tiene valores en MAYÚSCULAS: 'DESAYUNO', 'ALMUERZO', 'CENA'
    if 'tiempo_comida' in datos and isinstance(datos['tiempo_comida'], str):
        from models.programacion import TiempoComida
        try:
            tiempo_lower = datos['tiempo_comida'].lower().strip()
            tiempo_upper = datos['tiempo_comida'].upper().strip()
            # Buscar por valor (minúsculas) y convertir a nombre (mayúsculas)
            tiempo_encontrado = None
            for tiempo in TiempoComida:
                if tiempo.value == tiempo_lower:
                    tiempo_encontrado = tiempo
                    break
            if not tiempo_encontrado:
                # Si no se encuentra por valor, intentar por nombre
                tiempo_encontrado = TiempoComida[tiempo_upper]
            # Usar el NOMBRE del enum (mayúsculas) para PostgreSQL
            datos['tiempo_comida'] = tiempo_encontrado.name
        except (KeyError, AttributeError):
            return error_response(f"tiempo_comida inválido: {datos['tiempo_comida']}", 400, 'VALIDATION_ERROR')
    
    programacion = ProgramacionMenuService.crear_programacion(db.session, datos)
    
    # Verificar programación y generar tickets si faltan items/proveedores
    try:
        TicketsAutomaticosService.verificar_proveedores_items_insuficientes(
            db.session,
            programacion.id
        )
    except Exception as e:
        pass  # No crítico, continuar
    
    # Generar pedidos automáticamente después de crear la programación
    pedidos_generados = []
    try:
        usuario_id = datos.get('usuario_id', 1)
        pedidos_generados = PedidosAutomaticosService.generar_pedidos_desde_programacion(
            db.session,
            fecha_inicio=programacion.fecha_desde,
            usuario_id=usuario_id
        )
    except Exception as e:
        pass  # No crítico, continuar
    
    db.session.commit()
    
    return success_response({
        'programacion': programacion.to_dict(),
        'pedidos_generados': len(pedidos_generados),
        'pedidos': [p.to_dict() for p in pedidos_generados]
    }, 201, 'Programación creada correctamente')

@bp.route('/programacion/<int:programacion_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_programacion(programacion_id):
    """Actualiza una programación de menú existente."""
    validate_positive_int(programacion_id, 'programacion_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Convertir fechas string a date
    # Si viene 'fecha', usar para ambas fechas
    if 'fecha' in datos and isinstance(datos['fecha'], str):
        fecha = parse_date(datos['fecha'])
        if 'fecha_desde' not in datos or not datos['fecha_desde']:
            datos['fecha_desde'] = fecha
        if 'fecha_hasta' not in datos or not datos['fecha_hasta']:
            datos['fecha_hasta'] = fecha
    
    # Convertir fecha_desde y fecha_hasta si vienen como strings
    if 'fecha_desde' in datos and isinstance(datos['fecha_desde'], str):
        datos['fecha_desde'] = parse_date(datos['fecha_desde'])
    
    if 'fecha_hasta' in datos and isinstance(datos['fecha_hasta'], str):
        datos['fecha_hasta'] = parse_date(datos['fecha_hasta'])
    
    # Validar que fecha_hasta >= fecha_desde
    if datos.get('fecha_desde') and datos.get('fecha_hasta'):
        if datos['fecha_hasta'] < datos['fecha_desde']:
            return error_response('fecha_hasta debe ser mayor o igual a fecha_desde', 400, 'VALIDATION_ERROR')
    
    # Asegurar que 'fecha' tenga un valor si no viene (usar fecha_desde como fallback)
    # Esto es necesario porque la columna 'fecha' tiene NOT NULL en la BD
    if 'fecha' not in datos or datos['fecha'] is None:
        if datos.get('fecha_desde'):
            datos['fecha'] = datos['fecha_desde']
        # Si no hay fecha_desde, el servicio manejará el fallback usando la programación existente
    
    programacion = ProgramacionMenuService.actualizar_programacion(
        db.session,
        programacion_id,
        datos
    )
    db.session.commit()
    
    return success_response(programacion.to_dict(), message='Programación actualizada correctamente')

@bp.route('/programacion/<int:programacion_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_programacion(programacion_id):
    """Elimina una programación de menú."""
    validate_positive_int(programacion_id, 'programacion_id')
    
    programacion = db.query(ProgramacionMenu).filter(
        ProgramacionMenu.id == programacion_id
    ).first()
    
    if not programacion:
        return error_response('Programación no encontrada', 404, 'NOT_FOUND')
    
    # Eliminar items de programación primero (cascade debería hacerlo, pero por seguridad)
    db.query(ProgramacionMenuItem).filter(
        ProgramacionMenuItem.programacion_id == programacion_id
    ).delete()
    
    # Eliminar la programación
    db.delete(programacion)
    db.session.commit()
    
    return success_response(None, message='Programación eliminada correctamente')

@bp.route('/programacion/<int:programacion_id>/necesidades', methods=['GET'])
def calcular_necesidades(programacion_id):
    """Calcula las necesidades de items para una programación."""
    try:
        validate_positive_int(programacion_id, 'programacion_id')
        necesidades = ProgramacionMenuService.calcular_necesidades(db.session, programacion_id)
        return success_response(necesidades)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/programacion/<int:programacion_id>/generar-pedidos', methods=['POST'])
@handle_db_transaction
def generar_pedidos_automaticos(programacion_id):
    """Genera pedidos automáticos para items faltantes de una programación."""
    validate_positive_int(programacion_id, 'programacion_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    usuario_id = require_field(datos, 'usuario_id', int)
    
    pedidos = ProgramacionMenuService.generar_pedidos_automaticos(
        db.session,
        programacion_id,
        usuario_id
    )
    db.session.commit()
    
    return success_response(pedidos, 201, f'{len(pedidos)} pedidos generados correctamente')

@bp.route('/programacion/<int:programacion_id>/generar-pedidos-inteligentes', methods=['POST'])
@handle_db_transaction
def generar_pedidos_inteligentes(programacion_id):
    """
    Genera pedidos inteligentes para una programación:
    1. Primero compra lo necesario para la programación
    2. Luego asegura el inventario de emergencia/base (stock mínimo)
    """
    validate_positive_int(programacion_id, 'programacion_id')
    datos = request.get_json() or {}
    usuario_id = datos.get('usuario_id', 1)
    
    resultado = ProgramacionMenuService.generar_pedidos_inteligentes(
        db.session,
        programacion_id,
        usuario_id
    )
    db.session.commit()
    
    return success_response(resultado, 201, 'Pedidos inteligentes generados correctamente')
