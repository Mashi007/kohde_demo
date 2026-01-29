"""
Rutas API para módulo CRM.
Incluye: Proveedores, Tickets y Notificaciones
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models import db
from modules.crm.tickets import TicketService
from modules.crm.proveedores import ProveedorService

bp = Blueprint('crm', __name__)

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

# ========== RUTAS DE TICKETS ==========

@bp.route('/tickets', methods=['GET'])
def listar_tickets():
    """Lista tickets con filtros opcionales."""
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        estado = request.args.get('estado')
        tipo = request.args.get('tipo')
        asignado_a = request.args.get('asignado_a', type=int)
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        tickets = TicketService.listar_tickets(
            db.session,
            cliente_id=cliente_id,
            estado=estado,
            tipo=tipo,
            asignado_a=asignado_a,
            skip=skip,
            limit=limit
        )
        
        return jsonify([t.to_dict() for t in tickets]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/tickets', methods=['POST'])
def crear_ticket():
    """Crea un nuevo ticket."""
    try:
        datos = request.get_json()
        ticket = TicketService.crear_ticket(db.session, datos)
        return jsonify(ticket.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def obtener_ticket(ticket_id):
    """Obtiene un ticket por ID."""
    ticket = TicketService.obtener_ticket(db.session, ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket no encontrado'}), 404
    return jsonify(ticket.to_dict()), 200

@bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
def actualizar_ticket(ticket_id):
    """Actualiza un ticket existente."""
    try:
        datos = request.get_json()
        ticket = TicketService.actualizar_ticket(db.session, ticket_id, datos)
        return jsonify(ticket.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tickets/<int:ticket_id>/asignar', methods=['POST'])
def asignar_ticket(ticket_id):
    """Asigna un ticket a un usuario."""
    try:
        datos = request.get_json()
        usuario_id = datos.get('usuario_id')
        if not usuario_id:
            return jsonify({'error': 'usuario_id requerido'}), 400
        
        ticket = TicketService.asignar_ticket(db.session, ticket_id, usuario_id)
        return jsonify(ticket.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tickets/<int:ticket_id>/resolver', methods=['POST'])
def resolver_ticket(ticket_id):
    """Resuelve un ticket con una respuesta."""
    try:
        datos = request.get_json()
        respuesta = datos.get('respuesta')
        if not respuesta:
            return jsonify({'error': 'respuesta requerida'}), 400
        
        ticket = TicketService.resolver_ticket(db.session, ticket_id, respuesta)
        
        # Notificar por WhatsApp si se implementa en el futuro
        try:
            from modules.crm.notificaciones.whatsapp import whatsapp_service
            # Notificación opcional si se implementa
        except Exception as e:
            print(f"Error al enviar notificación: {e}")
        
        return jsonify(ticket.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
