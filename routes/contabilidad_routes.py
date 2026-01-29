"""
Rutas API para módulo de Contabilidad.
Nota: Facturas ahora está en el módulo Logística.
"""
from flask import Blueprint, request, jsonify
from models import db
from modules.contabilidad.centro_cuentas import CuentaContableService
from utils.route_helpers import (
    handle_db_transaction, require_field,
    validate_positive_int, success_response,
    error_response
)

bp = Blueprint('contabilidad', __name__)

# ========== RUTAS DE PLAN CONTABLE ==========

@bp.route('/cuentas', methods=['GET'])
def listar_cuentas():
    """Lista cuentas contables."""
    try:
        tipo = request.args.get('tipo')
        padre_id = request.args.get('padre_id', type=int)
        
        if padre_id:
            validate_positive_int(padre_id, 'padre_id')
        
        cuentas = CuentaContableService.listar_cuentas(
            db.session,
            tipo=tipo,
            padre_id=padre_id
        )
        
        return success_response([c.to_dict() for c in cuentas])
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/cuentas/arbol', methods=['GET'])
def obtener_arbol_cuentas():
    """Obtiene el árbol completo de cuentas contables."""
    try:
        arbol = CuentaContableService.obtener_arbol_cuentas(db.session)
        return success_response(arbol)
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/cuentas', methods=['POST'])
@handle_db_transaction
def crear_cuenta():
    """Crea una nueva cuenta contable."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    cuenta = CuentaContableService.crear_cuenta(db.session, datos)
    db.session.commit()
    return success_response(cuenta.to_dict(), 201, 'Cuenta creada correctamente')

@bp.route('/cuentas/<int:cuenta_id>', methods=['GET'])
def obtener_cuenta(cuenta_id):
    """Obtiene una cuenta contable por ID."""
    try:
        validate_positive_int(cuenta_id, 'cuenta_id')
        cuenta = CuentaContableService.obtener_cuenta(db.session, cuenta_id)
        if not cuenta:
            return error_response('Cuenta no encontrada', 404, 'NOT_FOUND')
        return success_response(cuenta.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')
