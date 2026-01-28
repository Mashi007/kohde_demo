"""
Rutas API para módulo de Compras.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.compras.proveedores import ProveedorService
from modules.compras.pedidos import PedidoCompraService

bp = Blueprint('compras', __name__)

# ========== RUTAS DE PROVEEDORES ==========

@bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """Lista proveedores con filtros opcionales."""
    try:
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        activo_bool = None if activo is None else activo.lower() == 'true'
        
        proveedores = ProveedorService.listar_proveedores(
            db.session,
            activo=activo_bool,
            busqueda=busqueda,
            skip=skip,
            limit=limit
        )
        
        return jsonify([p.to_dict() for p in proveedores]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/proveedores', methods=['POST'])
def crear_proveedor():
    """Crea un nuevo proveedor."""
    try:
        datos = request.get_json()
        proveedor = ProveedorService.crear_proveedor(db.session, datos)
        return jsonify(proveedor.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/proveedores/<int:proveedor_id>', methods=['GET'])
def obtener_proveedor(proveedor_id):
    """Obtiene un proveedor por ID."""
    proveedor = ProveedorService.obtener_proveedor(db.session, proveedor_id)
    if not proveedor:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    return jsonify(proveedor.to_dict()), 200

@bp.route('/proveedores/<int:proveedor_id>/facturas', methods=['GET'])
def obtener_facturas_proveedor(proveedor_id):
    """Obtiene el historial de facturas de un proveedor."""
    facturas = ProveedorService.obtener_historial_facturas(db.session, proveedor_id)
    return jsonify([f.to_dict() for f in facturas]), 200

@bp.route('/proveedores/<int:proveedor_id>/pedidos', methods=['GET'])
def obtener_pedidos_proveedor(proveedor_id):
    """Obtiene el historial de pedidos de un proveedor."""
    pedidos = ProveedorService.obtener_historial_pedidos(db.session, proveedor_id)
    return jsonify([p.to_dict() for p in pedidos]), 200

# ========== RUTAS DE PEDIDOS ==========

@bp.route('/pedidos', methods=['GET'])
def listar_pedidos():
    """Lista pedidos con filtros opcionales."""
    try:
        proveedor_id = request.args.get('proveedor_id', type=int)
        estado = request.args.get('estado')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        pedidos = PedidoCompraService.listar_pedidos(
            db.session,
            proveedor_id=proveedor_id,
            estado=estado,
            skip=skip,
            limit=limit
        )
        
        return jsonify([p.to_dict() for p in pedidos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/pedidos', methods=['POST'])
def crear_pedido():
    """Crea un nuevo pedido de compra."""
    try:
        datos = request.get_json()
        pedido = PedidoCompraService.crear_pedido(db.session, datos)
        return jsonify(pedido.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pedidos/automatico', methods=['POST'])
def generar_pedido_automatico():
    """Genera pedidos automáticos agrupados por proveedor."""
    try:
        datos = request.get_json()
        items_necesarios = datos.get('items_necesarios', [])
        usuario_id = datos.get('usuario_id')
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        pedidos = PedidoCompraService.generar_pedido_automatico(
            db.session,
            items_necesarios,
            usuario_id
        )
        
        return jsonify([p.to_dict() for p in pedidos]), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pedidos/<int:pedido_id>/enviar', methods=['POST'])
def enviar_pedido(pedido_id):
    """Envía un pedido al proveedor."""
    try:
        pedido = PedidoCompraService.enviar_pedido(db.session, pedido_id)
        return jsonify(pedido.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
