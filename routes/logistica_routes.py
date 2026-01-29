"""
Rutas API para módulo de Logística.
Incluye: Items, Inventario, Facturas, Compras y Pedidos
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from sqlalchemy import and_, exists
from models import db
from modules.logistica.items import ItemService
from modules.logistica.inventario import InventarioService
from modules.logistica.requerimientos import RequerimientoService
from modules.logistica.facturas import FacturaService
from modules.logistica.pedidos import PedidoCompraService
from modules.logistica.compras_stats import ComprasStatsService
from modules.logistica.costos import CostoService
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
        
        # Agregar costo promedio calculado a cada item
        items_con_costo = []
        for item in items:
            item_dict = item.to_dict()
            costo_promedio = ItemService.calcular_costo_unitario_promedio(db.session, item.id)
            item_dict['costo_unitario_promedio'] = costo_promedio
            items_con_costo.append(item_dict)
        
        return jsonify(items_con_costo), 200
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
    """Obtiene un item por ID con costo promedio calculado."""
    try:
        item = ItemService.obtener_item(db.session, item_id)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        
        item_dict = item.to_dict()
        costo_promedio = ItemService.calcular_costo_unitario_promedio(db.session, item_id)
        item_dict['costo_unitario_promedio'] = costo_promedio
        
        return jsonify(item_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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

@bp.route('/labels', methods=['POST'])
def crear_label():
    """Crea una nueva label/clasificación de alimentos."""
    try:
        from models.item_label import ItemLabel
        
        datos = request.get_json()
        
        # Validar campos requeridos
        if not datos.get('nombre_es'):
            return jsonify({'error': 'El nombre en español es requerido'}), 400
        if not datos.get('categoria_principal'):
            return jsonify({'error': 'La categoría principal es requerida'}), 400
        
        # Generar código si no se proporciona
        codigo = datos.get('codigo')
        if not codigo:
            # Generar código basado en categoría y nombre
            categoria_prefijo = datos['categoria_principal'][:3].upper().replace(' ', '_')
            nombre_prefijo = datos['nombre_es'][:5].upper().replace(' ', '_')
            codigo = f'{categoria_prefijo}_{nombre_prefijo}'
        
        # Verificar si ya existe una label con el mismo código
        existing = ItemLabel.query.filter_by(codigo=codigo).first()
        if existing:
            return jsonify({'error': f'Ya existe una clasificación con el código {codigo}'}), 400
        
        # Crear nueva label
        nueva_label = ItemLabel(
            codigo=codigo,
            nombre_es=datos['nombre_es'],
            nombre_en=datos.get('nombre_en', datos['nombre_es']),
            categoria_principal=datos['categoria_principal'],
            descripcion=datos.get('descripcion', ''),
            activo=datos.get('activo', True)
        )
        
        db.session.add(nueva_label)
        db.session.commit()
        
        return jsonify(nueva_label.to_dict()), 201
    except Exception as e:
        db.session.rollback()
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

@bp.route('/inventario/completo', methods=['GET'])
def obtener_inventario_completo():
    """Obtiene inventario completo con últimos movimientos."""
    try:
        inventario = InventarioService.obtener_inventario_completo_con_movimientos(db.session)
        return jsonify(inventario), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/inventario/dashboard', methods=['GET'])
def obtener_dashboard_inventario():
    """Obtiene resumen tipo dashboard del inventario."""
    try:
        resumen = InventarioService.obtener_resumen_dashboard(db.session)
        return jsonify(resumen), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/inventario/silos', methods=['GET'])
def obtener_silos_inventario():
    """Obtiene los top 10 items más comprados para visualización tipo silos."""
    try:
        silos = InventarioService.obtener_top_10_items_mas_comprados(db.session)
        return jsonify(silos), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        pendiente_confirmacion = request.args.get('pendiente_confirmacion', 'false').lower() == 'true'
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        query = db.session.query(Factura)
        
        if proveedor_id:
            query = query.filter(Factura.proveedor_id == proveedor_id)
        
        if cliente_id:
            query = query.filter(Factura.cliente_id == cliente_id)
        
        if estado:
            from models.factura import EstadoFactura
            try:
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
                    query = query.filter(Factura.estado == estado_enum)
                else:
                    # Intentar con el valor directamente en mayúsculas
                    try:
                        estado_enum = EstadoFactura[estado.upper()]
                        query = query.filter(Factura.estado == estado_enum)
                    except KeyError:
                        return jsonify({'error': f'Estado inválido: {estado}. Estados válidos: pendiente, parcial, aprobada, rechazada'}), 400
            except Exception as e:
                import traceback
                print(f"Error al filtrar por estado en facturas: {str(e)}")
                print(traceback.format_exc())
                return jsonify({'error': f'Error al procesar filtro de estado: {str(e)}'}), 500
        
        # Filtrar facturas pendientes de confirmación (con items sin cantidad_aprobada)
        if pendiente_confirmacion:
            from models import FacturaItem
            from models.factura import EstadoFactura as EstadoFacturaConfirmacion
            # Usar exists y and_ que ya están importados al inicio del archivo
            query = query.filter(
                Factura.estado == EstadoFacturaConfirmacion.PENDIENTE,
                exists().where(
                    and_(
                        FacturaItem.factura_id == Factura.id,
                        FacturaItem.cantidad_aprobada.is_(None)
                    )
                )
            )
        
        facturas = query.order_by(Factura.fecha_recepcion.desc()).offset(skip).limit(limit).all()
        
        return jsonify([f.to_dict() for f in facturas]), 200
    except KeyError as e:
        import traceback
        print(f"Error de clave en listar_facturas: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al procesar filtros: {str(e)}'}), 400
    except Exception as e:
        import traceback
        print(f"Error inesperado en listar_facturas: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/facturas/ultima', methods=['GET'])
def obtener_ultima_factura():
    """Obtiene la última factura ingresada."""
    try:
        from models import Factura
        factura = db.session.query(Factura).order_by(Factura.fecha_recepcion.desc()).first()
        if not factura:
            return jsonify(None), 200  # Retornar null en lugar de error 404
        try:
            factura_dict = factura.to_dict()
            return jsonify(factura_dict), 200
        except Exception as e:
            import traceback
            print(f"Error al serializar factura en obtener_ultima_factura: {str(e)}")
            print(traceback.format_exc())
            # Retornar datos básicos si hay error en to_dict()
            return jsonify({
                'id': factura.id,
                'numero_factura': factura.numero_factura,
                'estado': factura.estado.value if factura.estado else None,
                'error': 'Error al serializar datos completos'
            }), 200
    except Exception as e:
        import traceback
        print(f"Error en obtener_ultima_factura: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

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
        observaciones = datos.get('observaciones')
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        factura = FacturaService.aprobar_factura(
            db.session,
            factura_id,
            items_aprobados,
            usuario_id,
            aprobar_parcial,
            observaciones
        )
        
        return jsonify(factura.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/facturas/<int:factura_id>/rechazar', methods=['POST'])
def rechazar_factura(factura_id):
    """Rechaza una factura."""
    try:
        datos = request.get_json()
        usuario_id = datos.get('usuario_id')
        motivo = datos.get('motivo', 'Factura rechazada')
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        factura = FacturaService.rechazar_factura(
            db.session,
            factura_id,
            usuario_id,
            motivo
        )
        
        return jsonify(factura.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/facturas/<int:factura_id>/revision', methods=['POST'])
def enviar_a_revision(factura_id):
    """Envía una factura a revisión."""
    try:
        datos = request.get_json()
        usuario_id = datos.get('usuario_id')
        observaciones = datos.get('observaciones', '')
        
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        factura = FacturaService.enviar_a_revision(
            db.session,
            factura_id,
            usuario_id,
            observaciones
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

# ========== RUTAS DE COSTOS ESTANDARIZADOS ==========

@bp.route('/costos', methods=['GET'])
def listar_costos():
    """Lista costos estandarizados con filtros opcionales."""
    try:
        label_id = request.args.get('label_id', type=int)
        categoria = request.args.get('categoria')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        costos = CostoService.listar_costos_estandarizados(
            db.session,
            label_id=label_id,
            categoria=categoria,
            skip=skip,
            limit=limit
        )
        
        return jsonify([c.to_dict() for c in costos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/costos/<int:item_id>', methods=['GET'])
def obtener_costo_item(item_id):
    """Obtiene el costo estandarizado de un item específico."""
    try:
        costo = CostoService.obtener_costo_estandarizado(db.session, item_id)
        if not costo:
            return jsonify({'error': 'Costo no encontrado para este item'}), 404
        return jsonify(costo.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/costos/<int:item_id>/calcular', methods=['POST'])
def calcular_costo_item(item_id):
    """Calcula y almacena el costo estandarizado de un item."""
    try:
        costo = CostoService.calcular_y_almacenar_costo_estandarizado(db.session, item_id)
        if not costo:
            return jsonify({'error': 'No hay suficientes facturas aprobadas para calcular el costo'}), 404
        return jsonify(costo.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/costos/recalcular-todos', methods=['POST'])
def recalcular_todos_costos():
    """Recalcula todos los costos estandarizados de items y recetas."""
    try:
        estadisticas = CostoService.recalcular_todos_los_costos(db.session)
        return jsonify({
            'mensaje': 'Recálculo completado',
            'estadisticas': estadisticas
        }), 200
    except Exception as e:
        import traceback
        print(f"Error en recalcular_todos_costos: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/costos/recetas', methods=['GET'])
def listar_costos_recetas():
    """Lista costos de recetas con filtros opcionales."""
    try:
        from models import Receta
        from models.receta import TipoReceta
        
        tipo = request.args.get('tipo')
        activa = request.args.get('activa')
        busqueda = request.args.get('busqueda')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
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
        
        recetas = query.order_by(Receta.nombre).offset(skip).limit(limit).all()
        
        # Recalcular costos antes de retornar (por si acaso)
        for receta in recetas:
            receta.calcular_totales()
        
        db.commit()
        
        resultado = []
        for receta in recetas:
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
        
        return jsonify(resultado), 200
    except Exception as e:
        import traceback
        print(f"Error en listar_costos_recetas: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
