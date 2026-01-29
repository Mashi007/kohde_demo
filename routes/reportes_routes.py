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
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if fecha_fin:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        charolas = CharolaService.listar_charolas(
            db.session,
            fecha_inicio=fecha_inicio_obj,
            fecha_fin=fecha_fin_obj,
            ubicacion=ubicacion,
            tiempo_comida=tiempo_comida,
            skip=skip,
            limit=limit
        )
        
        return jsonify([c.to_dict() for c in charolas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/charolas', methods=['POST'])
def crear_charola():
    """Crea una nueva charola."""
    try:
        datos = request.get_json()
        
        # Convertir fecha_servicio si viene como string
        if 'fecha_servicio' in datos and isinstance(datos['fecha_servicio'], str):
            datos['fecha_servicio'] = datetime.fromisoformat(datos['fecha_servicio'].replace('Z', '+00:00'))
        
        charola = CharolaService.crear_charola(db.session, datos)
        
        # Verificar límites y generar tickets automáticos
        try:
            fecha_servicio = charola.fecha_servicio.date() if hasattr(charola.fecha_servicio, 'date') else datetime.now().date()
            TicketsAutomaticosService.verificar_charolas_vs_planificacion(db.session, fecha_servicio)
        except Exception as e:
            print(f"Error al verificar charolas automáticas: {e}")
        
        return jsonify(charola.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/charolas/<int:charola_id>', methods=['GET'])
def obtener_charola(charola_id):
    """Obtiene una charola por ID."""
    charola = CharolaService.obtener_charola(db.session, charola_id)
    if not charola:
        return jsonify({'error': 'Charola no encontrada'}), 404
    return jsonify(charola.to_dict()), 200

@bp.route('/charolas/resumen', methods=['GET'])
def obtener_resumen_charolas():
    """Obtiene resumen de charolas en un período."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        ubicacion = request.args.get('ubicacion')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'fecha_inicio y fecha_fin requeridos'}), 400
        
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        resumen = CharolaService.obtener_resumen_periodo(
            db.session,
            fecha_inicio_obj,
            fecha_fin_obj,
            ubicacion=ubicacion
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        fecha_inicio_obj = None
        fecha_fin_obj = None
        
        if fecha_inicio:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        if fecha_fin:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
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
        
        return jsonify([m.to_dict() for m in mermas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/mermas', methods=['POST'])
def crear_merma():
    """Crea una nueva merma."""
    try:
        datos = request.get_json()
        
        # Convertir fecha_merma si viene como string
        if 'fecha_merma' in datos and isinstance(datos['fecha_merma'], str):
            datos['fecha_merma'] = datetime.fromisoformat(datos['fecha_merma'].replace('Z', '+00:00'))
        
        merma = MermaService.crear_merma(db.session, datos)
        
        # Verificar límites y generar tickets automáticos
        try:
            fecha_merma = merma.fecha_merma.date() if hasattr(merma.fecha_merma, 'date') else datetime.now().date()
            TicketsAutomaticosService.verificar_mermas_limites(db.session, fecha_merma)
        except Exception as e:
            print(f"Error al verificar mermas automáticas: {e}")
        
        return jsonify(merma.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/mermas/<int:merma_id>', methods=['GET'])
def obtener_merma(merma_id):
    """Obtiene una merma por ID."""
    merma = MermaService.obtener_merma(db.session, merma_id)
    if not merma:
        return jsonify({'error': 'Merma no encontrada'}), 404
    return jsonify(merma.to_dict()), 200

@bp.route('/mermas/resumen', methods=['GET'])
def obtener_resumen_mermas():
    """Obtiene resumen de mermas en un período."""
    try:
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        ubicacion = request.args.get('ubicacion')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'error': 'fecha_inicio y fecha_fin requeridos'}), 400
        
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        
        resumen = MermaService.obtener_resumen_periodo(
            db.session,
            fecha_inicio_obj,
            fecha_fin_obj,
            ubicacion=ubicacion
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
