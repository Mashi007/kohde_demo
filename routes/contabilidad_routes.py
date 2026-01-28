"""
Rutas API para módulo de Contabilidad.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from models import db
from modules.contabilidad.ingreso_facturas import FacturaService
from modules.contabilidad.centro_cuentas import CuentaContableService
from config import Config

bp = Blueprint('contabilidad', __name__)

# ========== RUTAS DE FACTURAS ==========

@bp.route('/facturas', methods=['GET'])
def listar_facturas():
    """Lista facturas con filtros opcionales."""
    try:
        from models import Factura
        from sqlalchemy import and_
        
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

# ========== RUTAS DE PLAN CONTABLE ==========

@bp.route('/cuentas', methods=['GET'])
def listar_cuentas():
    """Lista cuentas contables."""
    try:
        tipo = request.args.get('tipo')
        padre_id = request.args.get('padre_id', type=int)
        
        cuentas = CuentaContableService.listar_cuentas(
            db.session,
            tipo=tipo,
            padre_id=padre_id
        )
        
        return jsonify([c.to_dict() for c in cuentas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/cuentas/arbol', methods=['GET'])
def obtener_arbol_cuentas():
    """Obtiene el árbol completo de cuentas contables."""
    try:
        arbol = CuentaContableService.obtener_arbol_cuentas(db.session)
        return jsonify(arbol), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/cuentas', methods=['POST'])
def crear_cuenta():
    """Crea una nueva cuenta contable."""
    try:
        datos = request.get_json()
        cuenta = CuentaContableService.crear_cuenta(db.session, datos)
        return jsonify(cuenta.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/cuentas/<int:cuenta_id>', methods=['GET'])
def obtener_cuenta(cuenta_id):
    """Obtiene una cuenta contable por ID."""
    cuenta = CuentaContableService.obtener_cuenta(db.session, cuenta_id)
    if not cuenta:
        return jsonify({'error': 'Cuenta no encontrada'}), 404
    return jsonify(cuenta.to_dict()), 200
