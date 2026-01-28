"""
Rutas API para módulo de Logística.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.logistica.items import ItemService
from modules.logistica.inventario import InventarioService
from modules.logistica.requerimientos import RequerimientoService

bp = Blueprint('logistica', __name__)

# ========== RUTAS DE ITEMS ==========

@bp.route('/items', methods=['GET'])
def listar_items():
    """Lista items con filtros opcionales."""
    try:
        categoria = request.args.get('categoria')
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        activo_bool = None if activo is None else activo.lower() == 'true'
        
        items = ItemService.listar_items(
            db.session,
            categoria=categoria,
            activo=activo_bool,
            busqueda=busqueda,
            skip=skip,
            limit=limit
        )
        
        return jsonify([i.to_dict() for i in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/items', methods=['POST'])
def crear_item():
    """Crea un nuevo item."""
    try:
        datos = request.get_json()
        item = ItemService.crear_item(db.session, datos)
        return jsonify(item.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/items/<int:item_id>', methods=['GET'])
def obtener_item(item_id):
    """Obtiene un item por ID."""
    item = ItemService.obtener_item(db.session, item_id)
    if not item:
        return jsonify({'error': 'Item no encontrado'}), 404
    return jsonify(item.to_dict()), 200

@bp.route('/items/<int:item_id>', methods=['PUT'])
def actualizar_item(item_id):
    """Actualiza un item existente."""
    try:
        datos = request.get_json()
        item = ItemService.actualizar_item(db.session, item_id, datos)
        return jsonify(item.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/items/<int:item_id>/costo', methods=['PUT'])
def actualizar_costo_item(item_id):
    """Actualiza el costo unitario de un item."""
    try:
        datos = request.get_json()
        costo = float(datos.get('costo'))
        item = ItemService.actualizar_costo_unitario(db.session, item_id, costo)
        return jsonify(item.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== RUTAS DE INVENTARIO ==========

@bp.route('/inventario', methods=['GET'])
def listar_inventario():
    """Lista el inventario completo o de un item específico."""
    try:
        item_id = request.args.get('item_id', type=int)
        inventario = InventarioService.obtener_inventario(db.session, item_id=item_id)
        return jsonify([inv.to_dict() for inv in inventario]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/inventario/stock-bajo', methods=['GET'])
def obtener_stock_bajo():
    """Obtiene items con stock bajo."""
    try:
        items = InventarioService.obtener_stock_bajo(db.session)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/inventario/<int:item_id>/verificar', methods=['POST'])
def verificar_disponibilidad(item_id):
    """Verifica disponibilidad de stock para un item."""
    try:
        datos = request.get_json()
        cantidad_necesaria = float(datos.get('cantidad_necesaria', 0))
        
        disponibilidad = InventarioService.verificar_disponibilidad(
            db.session,
            item_id,
            cantidad_necesaria
        )
        
        return jsonify(disponibilidad), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== RUTAS DE REQUERIMIENTOS ==========

@bp.route('/requerimientos', methods=['GET'])
def listar_requerimientos():
    """Lista requerimientos con filtros opcionales."""
    try:
        estado = request.args.get('estado')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        requerimientos = RequerimientoService.listar_requerimientos(
            db.session,
            estado=estado,
            skip=skip,
            limit=limit
        )
        
        return jsonify([r.to_dict() for r in requerimientos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/requerimientos', methods=['POST'])
def crear_requerimiento():
    """Crea un nuevo requerimiento."""
    try:
        datos = request.get_json()
        requerimiento = RequerimientoService.crear_requerimiento(db.session, datos)
        return jsonify(requerimiento.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/requerimientos/<int:requerimiento_id>/procesar', methods=['POST'])
def procesar_requerimiento(requerimiento_id):
    """Procesa un requerimiento entregando items y actualizando inventario."""
    try:
        requerimiento = RequerimientoService.procesar_requerimiento(
            db.session,
            requerimiento_id
        )
        return jsonify(requerimiento.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
