"""
Rutas API para módulo de Planificación.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
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
        
        return paginated_response([r.to_dict() for r in recetas], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

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

# ========== RUTAS DE PROGRAMACIÓN ==========

@bp.route('/programacion', methods=['GET'])
def listar_programaciones():
    """Lista programaciones con filtros opcionales."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        ubicacion = request.args.get('ubicacion')
        tiempo_comida = request.args.get('tiempo_comida')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        fecha_desde_obj = parse_date(fecha_desde) if fecha_desde else None
        fecha_hasta_obj = parse_date(fecha_hasta) if fecha_hasta else None
        
        programaciones = ProgramacionMenuService.listar_programaciones(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            ubicacion=ubicacion,
            tiempo_comida=tiempo_comida,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([p.to_dict() for p in programaciones], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/programacion', methods=['POST'])
@handle_db_transaction
def crear_programacion():
    """Crea una nueva programación de menú y genera pedidos automáticamente."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Convertir fecha string a date
    if 'fecha' in datos and isinstance(datos['fecha'], str):
        datos['fecha'] = parse_date(datos['fecha'])
    
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
            fecha_inicio=programacion.fecha,
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
    
    # Convertir fecha string a date si existe
    if 'fecha' in datos and isinstance(datos['fecha'], str):
        datos['fecha'] = parse_date(datos['fecha'])
    
    programacion = ProgramacionMenuService.actualizar_programacion(
        db.session,
        programacion_id,
        datos
    )
    db.session.commit()
    
    return success_response(programacion.to_dict(), message='Programación actualizada correctamente')

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
