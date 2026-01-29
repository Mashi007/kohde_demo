"""
Rutas API para módulo de Logística.
Incluye: Items, Inventario, Facturas, Compras y Pedidos
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from models import db
from modules.logistica.items import ItemService
from modules.logistica.inventario import InventarioService
from modules.logistica.requerimientos import RequerimientoService
from modules.logistica.facturas import FacturaService
from modules.logistica.pedidos import PedidoCompraService
from modules.logistica.compras_stats import ComprasStatsService
from models import ItemLabel
from config import Config
from datetime import datetime

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

# ========== RUTAS DE LABELS ==========

@bp.route('/labels', methods=['GET'])
def listar_labels():
    """Lista todas las labels disponibles."""
    try:
        categoria = request.args.get('categoria_principal')
        activo = request.args.get('activo', 'true')
        
        query = db.session.query(ItemLabel)
        
        if categoria:
            query = query.filter(ItemLabel.categoria_principal == categoria)
        
        if activo.lower() == 'true':
            query = query.filter(ItemLabel.activo == True)
        
        labels = query.order_by(ItemLabel.categoria_principal, ItemLabel.nombre_es).all()
        return jsonify([l.to_dict() for l in labels]), 200
    except Exception as e:
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

# ========== RUTAS DE PEDIDOS AUTOMÁTICOS ==========

@bp.route('/pedidos/aprobar/<int:pedido_id>', methods=['POST'])
def aprobar_pedido(pedido_id):
    """Aprueba un pedido y programa el envío automático 1 hora después."""
    try:
        from modules.logistica.pedidos_automaticos import PedidosAutomaticosService
        datos = request.get_json()
        usuario_id = datos.get('usuario_id', 1)
        
        pedido = PedidosAutomaticosService.aprobar_y_programar_envio(
            db.session,
            pedido_id,
            usuario_id
        )
        
        return jsonify({
            'mensaje': 'Pedido aprobado. Se enviará automáticamente en 1 hora.',
            'pedido': pedido.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/pedidos/requerimientos-quincenales', methods=['GET'])
def calcular_requerimientos_quincenales():
    """Calcula requerimientos quincenales basados en programación."""
    try:
        from modules.planificacion.requerimientos import RequerimientosService
        from datetime import date, timedelta
        
        fecha_inicio = request.args.get('fecha_inicio')
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        else:
            fecha_inicio = date.today()
        
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
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

# ========== RUTAS DE FACTURAS ==========

@bp.route('/facturas', methods=['GET'])
def listar_facturas():
    """Lista facturas con filtros opcionales."""
    try:
        from models import Factura
        
        proveedor_id = request.args.get('proveedor_id', type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        estado = request.args.get('estado')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        query = db.session.query(Factura)
        
        if proveedor_id:
            query = query.filter(Factura.proveedor_id == proveedor_id)
        
        if cliente_id:
            query = query.filter(Factura.cliente_id == cliente_id)
        
        if estado:
            from models.factura import EstadoFactura
            query = query.filter(Factura.estado == EstadoFactura[estado.upper()])
        
        facturas = query.order_by(Factura.fecha_recepcion.desc()).offset(skip).limit(limit).all()
        
        return jsonify([f.to_dict() for f in facturas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/facturas/ingresar-imagen', methods=['POST'])
def ingresar_factura_imagen():
    """Ingresa una factura desde una imagen usando OCR."""
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        archivo = request.files['imagen']
        tipo = request.form.get('tipo', 'proveedor')
        
        if archivo.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        
        # Guardar archivo temporalmente
        filename = secure_filename(archivo.filename)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, f"temp_{filename}")
        archivo.save(temp_path)
        
        try:
            # Procesar factura
            factura = FacturaService.procesar_factura_desde_imagen(
                db.session,
                temp_path,
                tipo=tipo
            )
            
            return jsonify(factura.to_dict()), 201
        finally:
            # Eliminar archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/facturas/<int:factura_id>', methods=['GET'])
def obtener_factura(factura_id):
    """Obtiene una factura por ID."""
    from models import Factura
    factura = db.session.query(Factura).filter(Factura.id == factura_id).first()
    if not factura:
        return jsonify({'error': 'Factura no encontrada'}), 404
    return jsonify(factura.to_dict()), 200

@bp.route('/facturas/<int:factura_id>/aprobar', methods=['POST'])
def aprobar_factura(factura_id):
    """Aprueba una factura y actualiza inventario."""
    try:
        datos = request.get_json()
        items_aprobados = datos.get('items_aprobados', [])
        usuario_id = datos.get('usuario_id')
        aprobar_parcial = datos.get('aprobar_parcial', False)
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        factura = FacturaService.aprobar_factura(
            db.session,
            factura_id,
            items_aprobados,
            usuario_id,
            aprobar_parcial
        )
        
        return jsonify(factura.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# ========== RUTAS DE ESTADÍSTICAS DE COMPRAS ==========

@bp.route('/compras/resumen', methods=['GET'])
def resumen_compras():
    """Obtiene resumen general de compras."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        resumen = ComprasStatsService.obtener_resumen_general(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/compras/por-item', methods=['GET'])
def compras_por_item():
    """Obtiene resumen de compras agrupado por item."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = int(request.args.get('limite', 20))
        
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        resumen = ComprasStatsService.obtener_resumen_por_item(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            limite=limite
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/compras/por-proveedor', methods=['GET'])
def compras_por_proveedor():
    """Obtiene resumen de compras agrupado por proveedor."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        limite = int(request.args.get('limite', 20))
        
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        resumen = ComprasStatsService.obtener_resumen_por_proveedor(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj,
            limite=limite
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/compras/por-proceso', methods=['GET'])
def compras_por_proceso():
    """Obtiene estadísticas de compras relacionadas con procesos de inventario y programación."""
    try:
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        fecha_desde_obj = None
        fecha_hasta_obj = None
        
        if fecha_desde:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        if fecha_hasta:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        
        resumen = ComprasStatsService.obtener_compras_por_proceso(
            db.session,
            fecha_desde=fecha_desde_obj,
            fecha_hasta=fecha_hasta_obj
        )
        
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
