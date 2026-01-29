"""
Rutas API para módulo de Contabilidad.
Nota: Facturas ahora está en el módulo Logística.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.contabilidad.centro_cuentas import CuentaContableService

bp = Blueprint('contabilidad', __name__)

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
