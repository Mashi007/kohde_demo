"""
Rutas API para módulo CRM.
Incluye: Proveedores, Notificaciones y Tickets
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models import db, Item
from modules.crm.tickets import TicketService
from modules.crm.tickets_automaticos import TicketsAutomaticosService
from modules.crm.proveedores import ProveedorService
from modules.crm.notificaciones.whatsapp import whatsapp_service
from modules.crm.notificaciones.email import email_service
from datetime import datetime
from utils.route_helpers import (
    handle_db_transaction, parse_date, require_field,
    validate_positive_int, success_response,
    error_response, paginated_response
)

bp = Blueprint('crm', __name__)

# ========== RUTAS DE PROVEEDORES ==========

@bp.route('/proveedores', methods=['GET'])
def listar_proveedores():
    """Lista proveedores con filtros opcionales."""
    try:
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        label_id = request.args.get('label_id', type=int)
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if label_id:
            validate_positive_int(label_id, 'label_id')
        
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
        
        return paginated_response(resultado, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/proveedores', methods=['POST'])
@handle_db_transaction
def crear_proveedor():
    """Crea un nuevo proveedor."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    proveedor = ProveedorService.crear_proveedor(db.session, datos)
    db.session.commit()
    return success_response(proveedor.to_dict(), 201, 'Proveedor creado correctamente')

@bp.route('/proveedores/<int:proveedor_id>', methods=['GET'])
def obtener_proveedor(proveedor_id):
    """Obtiene un proveedor por ID con items y labels."""
    try:
        validate_positive_int(proveedor_id, 'proveedor_id')
        resultado = ProveedorService.obtener_proveedor_con_items_labels(db.session, proveedor_id)
        if not resultado:
            return error_response('Proveedor no encontrado', 404, 'NOT_FOUND')
        return success_response(resultado)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/proveedores/<int:proveedor_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_proveedor(proveedor_id):
    """Actualiza un proveedor existente."""
    validate_positive_int(proveedor_id, 'proveedor_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    proveedor = ProveedorService.actualizar_proveedor(db.session, proveedor_id, datos)
    db.session.commit()
    return success_response(proveedor.to_dict(), message='Proveedor actualizado correctamente')

@bp.route('/proveedores/<int:proveedor_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_proveedor(proveedor_id):
    """Elimina (soft delete) un proveedor."""
    validate_positive_int(proveedor_id, 'proveedor_id')
    ProveedorService.eliminar_proveedor(db.session, proveedor_id)
    db.session.commit()
    return success_response(None, message='Proveedor eliminado correctamente')

@bp.route('/proveedores/<int:proveedor_id>/toggle-activo', methods=['POST'])
@handle_db_transaction
def toggle_activo_proveedor(proveedor_id):
    """Alterna el estado activo/inactivo de un proveedor."""
    validate_positive_int(proveedor_id, 'proveedor_id')
    proveedor = ProveedorService.toggle_activo(db.session, proveedor_id)
    db.session.commit()
    return success_response(proveedor.to_dict(), message='Estado actualizado correctamente')

@bp.route('/proveedores/<int:proveedor_id>/facturas', methods=['GET'])
def obtener_facturas_proveedor(proveedor_id):
    """Obtiene el historial de facturas de un proveedor."""
    try:
        validate_positive_int(proveedor_id, 'proveedor_id')
        facturas = ProveedorService.obtener_historial_facturas(db.session, proveedor_id)
        return success_response([f.to_dict() for f in facturas])
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/proveedores/<int:proveedor_id>/pedidos', methods=['GET'])
def obtener_pedidos_proveedor(proveedor_id):
    """Obtiene el historial de pedidos de un proveedor."""
    try:
        validate_positive_int(proveedor_id, 'proveedor_id')
        pedidos = ProveedorService.obtener_historial_pedidos(db.session, proveedor_id)
        return success_response([p.to_dict() for p in pedidos])
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

# ========== RUTAS DE NOTIFICACIONES ==========

@bp.route('/notificaciones', methods=['GET'])
def listar_notificaciones():
    """Lista notificaciones enviadas con filtros opcionales."""
    try:
        tipo = request.args.get('tipo')  # 'whatsapp' o 'email'
        destinatario = request.args.get('destinatario')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 50), 'limit')
        
        # Por ahora retornamos un resumen, en el futuro se puede guardar en BD
        notificaciones = []
        
        return paginated_response(notificaciones, total=0, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/enviar', methods=['POST'])
def enviar_notificacion():
    """Envía una notificación (WhatsApp o Email)."""
    try:
        datos = request.get_json()
        if not datos:
            return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
        
        tipo = datos.get('tipo')
        destinatario = datos.get('destinatario')
        mensaje = datos.get('mensaje')
        asunto = datos.get('asunto', '')
        
        if not tipo or not destinatario or not mensaje:
            return error_response('tipo, destinatario y mensaje son requeridos', 400, 'VALIDATION_ERROR')
        
        if tipo == 'whatsapp':
            resultado = whatsapp_service.enviar_mensaje(destinatario, mensaje)
            # WhatsApp API retorna: {"messages": [{"id": "wamid.xxx"}]}
            mensaje_id = None
            if isinstance(resultado, dict):
                messages = resultado.get('messages', [])
                if messages and len(messages) > 0:
                    mensaje_id = messages[0].get('id')
            
            return success_response({
                'tipo': 'whatsapp',
                'mensaje_id': mensaje_id
            }, message='Notificación WhatsApp enviada correctamente')
        
        elif tipo == 'email':
            # Convertir mensaje a HTML básico
            contenido_html = f"<p>{mensaje.replace(chr(10), '<br>')}</p>"
            resultado = email_service.enviar_email(
                destinatario,
                asunto or 'Notificación del Sistema',
                contenido_html,
                contenido_texto=mensaje
            )
            return success_response({
                'tipo': 'email'
            }, message='Notificación Email enviada correctamente')
        
        else:
            return error_response('Tipo de notificación no válido. Use "whatsapp" o "email"', 400, 'VALIDATION_ERROR')
            
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de notificaciones."""
    try:
        # Por ahora retornamos estadísticas básicas
        # En el futuro se puede consultar desde una tabla de notificaciones
        return success_response({
            'total_whatsapp': 0,
            'total_email': 0,
            'exitosas': 0,
            'fallidas': 0
        })
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

# ========== RUTAS DE TICKETS ==========

@bp.route('/tickets', methods=['GET'])
def listar_tickets():
    """Lista tickets con filtros opcionales."""
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        estado = request.args.get('estado')
        tipo = request.args.get('tipo')
        asignado_a = request.args.get('asignado_a', type=int)
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if cliente_id:
            validate_positive_int(cliente_id, 'cliente_id')
        if asignado_a:
            validate_positive_int(asignado_a, 'asignado_a')
        
        tickets = TicketService.listar_tickets(
            db.session,
            cliente_id=cliente_id,
            estado=estado,
            tipo=tipo,
            asignado_a=asignado_a,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([t.to_dict() for t in tickets], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets', methods=['POST'])
@handle_db_transaction
def crear_ticket():
    """Crea un nuevo ticket."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    ticket = TicketService.crear_ticket(db.session, datos)
    db.session.commit()
    return success_response(ticket.to_dict(), 201, 'Ticket creado correctamente')

@bp.route('/tickets/<int:ticket_id>', methods=['GET'])
def obtener_ticket(ticket_id):
    """Obtiene un ticket por ID."""
    try:
        validate_positive_int(ticket_id, 'ticket_id')
        ticket = TicketService.obtener_ticket(db.session, ticket_id)
        if not ticket:
            return error_response('Ticket no encontrado', 404, 'NOT_FOUND')
        return success_response(ticket.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_ticket(ticket_id):
    """Actualiza un ticket existente."""
    validate_positive_int(ticket_id, 'ticket_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    ticket = TicketService.actualizar_ticket(db.session, ticket_id, datos)
    db.session.commit()
    return success_response(ticket.to_dict(), message='Ticket actualizado correctamente')

@bp.route('/tickets/<int:ticket_id>/asignar', methods=['POST'])
@handle_db_transaction
def asignar_ticket(ticket_id):
    """Asigna un ticket a un usuario."""
    validate_positive_int(ticket_id, 'ticket_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    usuario_id = require_field(datos, 'usuario_id', int)
    ticket = TicketService.asignar_ticket(db.session, ticket_id, usuario_id)
    db.session.commit()
    return success_response(ticket.to_dict(), message='Ticket asignado correctamente')

@bp.route('/tickets/<int:ticket_id>/resolver', methods=['POST'])
@handle_db_transaction
def resolver_ticket(ticket_id):
    """Resuelve un ticket con una respuesta."""
    validate_positive_int(ticket_id, 'ticket_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    respuesta = require_field(datos, 'respuesta', str)
    
    ticket = TicketService.resolver_ticket(db.session, ticket_id, respuesta)
    db.session.commit()
    
    # Notificar por WhatsApp si se implementa en el futuro
    # whatsapp_service ya está importado al inicio del archivo
    
    return success_response(ticket.to_dict(), message='Ticket resuelto correctamente')

# ========== RUTAS DE TICKETS AUTOMÁTICOS ==========

@bp.route('/tickets/verificar-automaticos', methods=['POST'])
@handle_db_transaction
def verificar_tickets_automaticos():
    """Ejecuta todas las verificaciones automáticas y genera tickets."""
    try:
        datos = request.get_json() or {}
        fecha_str = datos.get('fecha')
        
        fecha = parse_date(fecha_str) if fecha_str else None
        
        resultado = TicketsAutomaticosService.ejecutar_verificaciones_completas(
            db.session,
            fecha=fecha
        )
        db.session.commit()
        
        return success_response(resultado)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/verificar-charolas', methods=['POST'])
@handle_db_transaction
def verificar_charolas():
    """Verifica charolas vs planificación y genera tickets."""
    try:
        datos = request.get_json() or {}
        fecha_str = datos.get('fecha')
        
        fecha = parse_date(fecha_str) if fecha_str else None
        
        tickets = TicketsAutomaticosService.verificar_charolas_vs_planificacion(
            db.session,
            fecha=fecha
        )
        db.session.commit()
        
        return success_response({
            'tickets_generados': len(tickets),
            'tickets': [t.to_dict() for t in tickets]
        })
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/verificar-mermas', methods=['POST'])
@handle_db_transaction
def verificar_mermas():
    """Verifica mermas contra límites y genera tickets."""
    try:
        datos = request.get_json() or {}
        fecha_str = datos.get('fecha')
        
        fecha = parse_date(fecha_str) if fecha_str else None
        
        tickets = TicketsAutomaticosService.verificar_mermas_limites(
            db.session,
            fecha=fecha
        )
        db.session.commit()
        
        return success_response({
            'tickets_generados': len(tickets),
            'tickets': [t.to_dict() for t in tickets]
        })
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/verificar-inventario', methods=['POST'])
@handle_db_transaction
def verificar_inventario():
    """Verifica inventario bajo mínimo y genera tickets."""
    try:
        tickets = TicketsAutomaticosService.verificar_inventario_seguridad(db.session)
        db.session.commit()
        
        return success_response({
            'tickets_generados': len(tickets),
            'tickets': [t.to_dict() for t in tickets]
        })
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/verificar-programacion', methods=['POST'])
@handle_db_transaction
def verificar_programacion():
    """Verifica programación faltante y genera tickets."""
    try:
        datos = request.get_json() or {}
        fecha_str = datos.get('fecha')
        
        fecha = parse_date(fecha_str) if fecha_str else None
        
        tickets = TicketsAutomaticosService.verificar_programacion_faltante(
            db.session,
            fecha=fecha
        )
        db.session.commit()
        
        return success_response({
            'tickets_generados': len(tickets),
            'tickets': [t.to_dict() for t in tickets]
        })
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/tickets/verificar-reportes', methods=['POST'])
@handle_db_transaction
def verificar_reportes():
    """Verifica reportes faltantes después del tiempo límite."""
    try:
        datos = request.get_json() or {}
        fecha_str = datos.get('fecha')
        
        fecha = parse_date(fecha_str) if fecha_str else None
        
        tickets = TicketsAutomaticosService.verificar_reportes_faltantes(
            db.session,
            fecha=fecha
        )
        db.session.commit()
        
        return success_response({
            'tickets_generados': len(tickets),
            'tickets': [t.to_dict() for t in tickets]
        })
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')
