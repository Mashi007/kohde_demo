"""
Rutas API para módulo CRM.
Incluye: Proveedores, Notificaciones y Tickets
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models import db, Item
from modules.crm.tickets import TicketService
from modules.crm.proveedores import ProveedorService
from modules.crm.notificaciones.whatsapp import whatsapp_service
from modules.crm.notificaciones.email import email_service

bp = Blueprint('crm', __name__)

# ========== RUTAS DE PROVEEDORES ==========

@bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """Lista proveedores con filtros opcionales."""
    try:
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        label_id = request.args.get('label_id', type=int)  # Filtrar por label
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))
        
        activo_bool = None if activo is None else activo.lower() == 'true'
        
        proveedores = ProveedorService.listar_proveedores(
            db.session,
            activo=activo_bool,
            busqueda=busqueda,
            label_id=label_id,
            skip=skip,
            limit=limit
        )
        
        # Incluir información de items y labels para cada proveedor
        resultado = []
        for p in proveedores:
            prov_dict = p.to_dict(include_items=True)
            resultado.append(prov_dict)
        
        return jsonify(resultado), 200
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
    """Obtiene un proveedor por ID con items y labels."""
    resultado = ProveedorService.obtener_proveedor_con_items_labels(db.session, proveedor_id)
    if not resultado:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    return jsonify(resultado), 200

@bp.route('/proveedores/<int:proveedor_id>', methods=['PUT'])
def actualizar_proveedor(proveedor_id):
    """Actualiza un proveedor existente."""
    try:
        datos = request.get_json()
        proveedor = ProveedorService.actualizar_proveedor(db.session, proveedor_id, datos)
        return jsonify(proveedor.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/proveedores/<int:proveedor_id>', methods=['DELETE'])
def eliminar_proveedor(proveedor_id):
    """Elimina (soft delete) un proveedor."""
    try:
        ProveedorService.eliminar_proveedor(db.session, proveedor_id)
        return jsonify({'mensaje': 'Proveedor eliminado correctamente'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/proveedores/<int:proveedor_id>/toggle-activo', methods=['POST'])
def toggle_activo_proveedor(proveedor_id):
    """Alterna el estado activo/inactivo de un proveedor."""
    try:
        proveedor = ProveedorService.toggle_activo(db.session, proveedor_id)
        return jsonify(proveedor.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

# ========== RUTAS DE NOTIFICACIONES ==========

@bp.route('/notificaciones', methods=['GET'])
def listar_notificaciones():
    """Lista notificaciones enviadas con filtros opcionales."""
    try:
        tipo = request.args.get('tipo')  # 'whatsapp' o 'email'
        destinatario = request.args.get('destinatario')
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))
        
        # Por ahora retornamos un resumen, en el futuro se puede guardar en BD
        notificaciones = []
        
        # Aquí se podría consultar una tabla de notificaciones si existe
        # Por ahora retornamos un array vacío o datos de ejemplo
        
        return jsonify({
            'notificaciones': notificaciones,
            'total': len(notificaciones),
            'skip': skip,
            'limit': limit
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/notificaciones/enviar', methods=['POST'])
def enviar_notificacion():
    """Envía una notificación (WhatsApp o Email)."""
    try:
        datos = request.get_json()
        tipo = datos.get('tipo')  # 'whatsapp' o 'email'
        destinatario = datos.get('destinatario')  # número o email
        mensaje = datos.get('mensaje')
        asunto = datos.get('asunto', '')  # Solo para email
        
        if not tipo or not destinatario or not mensaje:
            return jsonify({'error': 'tipo, destinatario y mensaje son requeridos'}), 400
        
        resultado = None
        
        if tipo == 'whatsapp':
            resultado = whatsapp_service.enviar_mensaje(destinatario, mensaje)
            # WhatsApp API retorna: {"messages": [{"id": "wamid.xxx"}]}
            mensaje_id = None
            if isinstance(resultado, dict):
                messages = resultado.get('messages', [])
                if messages and len(messages) > 0:
                    mensaje_id = messages[0].get('id')
            
            return jsonify({
                'exito': True,
                'tipo': 'whatsapp',
                'mensaje_id': mensaje_id,
                'mensaje': 'Notificación WhatsApp enviada correctamente'
            }), 200
        
        elif tipo == 'email':
            # Convertir mensaje a HTML básico
            contenido_html = f"<p>{mensaje.replace(chr(10), '<br>')}</p>"
            resultado = email_service.enviar_email(
                destinatario,
                asunto or 'Notificación del Sistema',
                contenido_html,
                contenido_texto=mensaje
            )
            return jsonify({
                'exito': True,
                'tipo': 'email',
                'mensaje': 'Notificación Email enviada correctamente'
            }), 200
        
        else:
            return jsonify({'error': 'Tipo de notificación no válido. Use "whatsapp" o "email"'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/notificaciones/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de notificaciones."""
    try:
        # Por ahora retornamos estadísticas básicas
        # En el futuro se puede consultar desde una tabla de notificaciones
        return jsonify({
            'total_whatsapp': 0,
            'total_email': 0,
            'exitosas': 0,
            'fallidas': 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
