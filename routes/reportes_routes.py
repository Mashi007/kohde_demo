"""
Rutas API para módulo de Reportes.
Incluye: Charolas y Mermas
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
from modules.reportes.charolas import CharolaService
from modules.reportes.mermas import MermaService
from modules.crm.tickets_automaticos import TicketsAutomaticosService
from utils.route_helpers import (
    handle_db_transaction, parse_date, parse_datetime, require_field,
    validate_positive_int, success_response,
    error_response, paginated_response
)

bp = Blueprint('reportes', __name__)

# ========== RUTAS DE CHAROLAS ==========

@bp.route('/charolas', methods=['GET'])
def listar_charolas():
    """Lista charolas con filtros opcionales."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        ubicacion = request.args.get('ubicacion')
        tiempo_comida = request.args.get('tiempo_comida')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        fecha_inicio_obj = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin_obj = parse_date(fecha_fin) if fecha_fin else None
        
        charolas = CharolaService.listar_charolas(
            db.session,
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj,
            ubicacion=ubicacion,
            tiempo_comida=tiempo_comida,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([c.to_dict() for c in charolas], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/charolas', methods=['POST'])
@handle_db_transaction
def crear_charola():
    """Crea una nueva charola."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Convertir fecha_servicio si viene como string
    if 'fecha_servicio' in datos and isinstance(datos['fecha_servicio'], str):
        datos['fecha_servicio'] = parse_datetime(datos['fecha_servicio'].replace('Z', '+00:00'))
    
    charola = CharolaService.crear_charola(db.session, datos)
    
    # Verificar límites y generar tickets automáticos
    try:
        fecha_servicio = charola.fecha_servicio.date() if hasattr(charola.fecha_servicio, 'date') else datetime.now().date()
        TicketsAutomaticosService.verificar_charolas_vs_planificacion(db.session, fecha_servicio)
    except Exception:
        pass  # No crítico
    
    db.session.commit()
    return success_response(charola.to_dict(), 201, 'Charola creada correctamente')

@bp.route('/charolas/<int:charola_id>', methods=['GET'])
def obtener_charola(charola_id):
    """Obtiene una charola por ID."""
    try:
        validate_positive_int(charola_id, 'charola_id')
        charola = CharolaService.obtener_charola(db.session, charola_id)
        if not charola:
            return error_response('Charola no encontrada', 404, 'NOT_FOUND')
        return success_response(charola.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/charolas/resumen', methods=['GET'])
def obtener_resumen_charolas():
    """Obtiene resumen de charolas en un período."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        ubicacion = request.args.get('ubicacion')
        
        if not fecha_inicio or not fecha_fin:
            return error_response('fecha_inicio y fecha_fin requeridos', 400, 'VALIDATION_ERROR')
        
        fecha_inicio_obj = parse_date(fecha_inicio)
        fecha_fin_obj = parse_date(fecha_fin)
        
        resumen = CharolaService.obtener_resumen_periodo(
            db.session,
            fecha_inicio_obj,
            fecha_fin_obj,
            ubicacion=ubicacion
        )
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

# ========== RUTAS DE MERMAS ==========

@bp.route('/mermas', methods=['GET'])
def listar_mermas():
    """Lista mermas con filtros opcionales."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        item_id = request.args.get('item_id', type=int)
        tipo = request.args.get('tipo')
        ubicacion = request.args.get('ubicacion')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if item_id:
            validate_positive_int(item_id, 'item_id')
        
        fecha_inicio_obj = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin_obj = parse_date(fecha_fin) if fecha_fin else None
        
        mermas = MermaService.listar_mermas(
            db.session,
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj,
            item_id=item_id,
            tipo=tipo,
            ubicacion=ubicacion,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([m.to_dict() for m in mermas], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/mermas', methods=['POST'])
@handle_db_transaction
def crear_merma():
    """Crea una nueva merma."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    # Convertir fecha_merma si viene como string
    if 'fecha_merma' in datos and isinstance(datos['fecha_merma'], str):
        datos['fecha_merma'] = parse_datetime(datos['fecha_merma'].replace('Z', '+00:00'))
    
    merma = MermaService.crear_merma(db.session, datos)
    
    # Verificar límites y generar tickets automáticos
    try:
        fecha_merma = merma.fecha_merma.date() if hasattr(merma.fecha_merma, 'date') else datetime.now().date()
        TicketsAutomaticosService.verificar_mermas_limites(db.session, fecha_merma)
    except Exception:
        pass  # No crítico
    
    db.session.commit()
    return success_response(merma.to_dict(), 201, 'Merma creada correctamente')

@bp.route('/mermas/<int:merma_id>', methods=['GET'])
def obtener_merma(merma_id):
    """Obtiene una merma por ID."""
    try:
        validate_positive_int(merma_id, 'merma_id')
        merma = MermaService.obtener_merma(db.session, merma_id)
        if not merma:
            return error_response('Merma no encontrada', 404, 'NOT_FOUND')
        return success_response(merma.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/mermas/resumen', methods=['GET'])
def obtener_resumen_mermas():
    """Obtiene resumen de mermas en un período."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        ubicacion = request.args.get('ubicacion')
        
        if not fecha_inicio or not fecha_fin:
            return error_response('fecha_inicio y fecha_fin requeridos', 400, 'VALIDATION_ERROR')
        
        fecha_inicio_obj = parse_date(fecha_inicio)
        fecha_fin_obj = parse_date(fecha_fin)
        
        resumen = MermaService.obtener_resumen_periodo(
            db.session,
            fecha_inicio_obj,
            fecha_fin_obj,
            ubicacion=ubicacion
        )
        
        return success_response(resumen)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')
