"""
Rutas API para módulo de Compras.
Nota: Este módulo está vacío. Proveedores está en CRM y Pedidos está en Logística.
Este archivo se mantiene por compatibilidad pero puede eliminarse en el futuro.
"""
from flask import Blueprint, request, jsonify

bp = Blueprint('compras', __name__)

@bp.route('/health', methods=['GET'])
def health():
    """Endpoint de salud para el módulo de Compras."""
    return jsonify({
        'message': 'Módulo de Compras vacío. Pedidos ahora está en Logística.',
        'pedidos_url': '/api/logistica/pedidos'
    }), 200
