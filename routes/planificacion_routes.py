"""
Rutas API para módulo de Planificación.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
from modules.planificacion.recetas import RecetaService
from modules.planificacion.programacion import ProgramacionMenuService
from modules.crm.tickets_automaticos import TicketsAutomaticosService

bp = Blueprint('planificacion', __name__)

# ========== RUTAS DE RECETAS ==========

@bp.route('/recetas', methods=['GET'])
def listar_recetas():
    """Lista recetas con filtros opcionales."""
    try:
        activa = request.args.get('activa')
        busqueda = request.args.get('busqueda')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        activa_bool = None if activa is None else activa.lower() == 'true'
        
        recetas = RecetaService.listar_recetas(
            db.session,
            activa=activa_bool,
            busqueda=busqueda,
            skip=skip,
            limit=limit
        )
        
        return jsonify([r.to_dict() for r in recetas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/recetas', methods=['POST'])
def crear_receta():
    """Crea una nueva receta."""
    try:
        datos = request.get_json()
        receta = RecetaService.crear_receta(db.session, datos)
        return jsonify(receta.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/recetas/<int:receta_id>', methods=['GET'])
def obtener_receta(receta_id):
    """Obtiene una receta por ID."""
    receta = RecetaService.obtener_receta(db.session, receta_id)
    if not receta:
        return jsonify({'error': 'Receta no encontrada'}), 404
    return jsonify(receta.to_dict()), 200

@bp.route('/recetas/<int:receta_id>', methods=['PUT'])
def actualizar_receta(receta_id):
    """Actualiza una receta existente."""
    try:
        datos = request.get_json()
        receta = RecetaService.actualizar_receta(db.session, receta_id, datos)
        return jsonify(receta.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/recetas/<int:receta_id>/duplicar', methods=['POST'])
def duplicar_receta(receta_id):
    """Duplica una receta existente."""
    try:
        datos = request.get_json()
        nuevo_nombre = datos.get('nuevo_nombre')
        if not nuevo_nombre:
            return jsonify({'error': 'nuevo_nombre requerido'}), 400
        
        receta = RecetaService.duplicar_receta(db.session, receta_id, nuevo_nombre)
        return jsonify(receta.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== RUTAS DE PROGRAMACIÓN ==========

@bp.route('/programacion', methods=['GET'])
def listar_programaciones():
    """Lista programaciones con filtros opcionales."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        ubicacion = request.args.get('ubicacion')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        programaciones = ProgramacionMenuService.listar_programaciones(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            ubicacion=ubicacion,
            skip=skip,
            limit=limit
        )
        
        return jsonify([p.to_dict() for p in programaciones]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/programacion', methods=['POST'])
def crear_programacion():
    """Crea una nueva programación de menú y genera pedidos automáticamente."""
    try:
        datos = request.get_json()
        # Convertir fecha string a date
        if 'fecha' in datos and isinstance(datos['fecha'], str):
            datos['fecha'] = datetime.strptime(datos['fecha'], '%Y-%m-%d').date()
        
        programacion = ProgramacionMenuService.crear_programacion(db.session, datos)
        
        # Verificar programación y generar tickets si faltan items/proveedores
        try:
            TicketsAutomaticosService.verificar_proveedores_items_insuficientes(
                db.session,
                programacion.id
            )
        except Exception as e:
            print(f"Error al verificar proveedores automáticos: {e}")
        
        # Generar pedidos automáticamente después de crear la programación
        try:
            from modules.logistica.pedidos_automaticos import PedidosAutomaticosService
            usuario_id = datos.get('usuario_id', 1)  # Por defecto usuario 1
            pedidos = PedidosAutomaticosService.generar_pedidos_desde_programacion(
                db.session,
                fecha_inicio=programacion.fecha,
                usuario_id=usuario_id
            )
            
            return jsonify({
                'programacion': programacion.to_dict(),
                'pedidos_generados': len(pedidos),
                'pedidos': [p.to_dict() for p in pedidos]
            }), 201
        except Exception as e:
            # Si falla la generación de pedidos, igual retornar la programación
            print(f"Error al generar pedidos automáticos: {e}")
            return jsonify({
                'programacion': programacion.to_dict(),
                'pedidos_generados': 0,
                'advertencia': 'Programación creada pero no se pudieron generar pedidos automáticos'
            }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/programacion/<int:programacion_id>/necesidades', methods=['GET'])
def calcular_necesidades(programacion_id):
    """Calcula las necesidades de items para una programación."""
    try:
        necesidades = ProgramacionMenuService.calcular_necesidades(db.session, programacion_id)
        return jsonify(necesidades), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/programacion/<int:programacion_id>/generar-pedidos', methods=['POST'])
def generar_pedidos_automaticos(programacion_id):
    """Genera pedidos automáticos para items faltantes de una programación."""
    try:
        datos = request.get_json()
        usuario_id = datos.get('usuario_id')
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        pedidos = ProgramacionMenuService.generar_pedidos_automaticos(
            db.session,
            programacion_id,
            usuario_id
        )
        
        return jsonify(pedidos), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
