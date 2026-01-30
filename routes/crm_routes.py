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
from modules.crm.contactos import contacto_service
from modules.crm.conversaciones import conversacion_service
from models.conversacion_contacto import TipoMensajeContacto
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
            try:
                # Obtener items del proveedor con eager loading de labels
                from sqlalchemy.orm import selectinload
                from models import Item
                
                items = db.session.query(Item).options(
                    selectinload(Item.labels)
                ).filter(
                    Item.proveedor_autorizado_id == p.id,
                    Item.activo == True
                ).all()
                
                # Contar labels únicos
                labels_set = set()
                for item in items:
                    for label in item.labels:
                        if label.activo:
                            labels_set.add(label.id)
                
                prov_dict = p.to_dict(include_items=False)
                prov_dict['total_items'] = len(items)
                prov_dict['total_labels'] = len(labels_set)
                
                resultado.append(prov_dict)
            except Exception as e:
                import logging
                logging.error(f"Error procesando proveedor {p.id}: {str(e)}", exc_info=True)
                # Si falla, agregar sin items
                prov_dict = p.to_dict(include_items=False)
                prov_dict['total_items'] = 0
                prov_dict['total_labels'] = 0
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
    """Lista notificaciones enviadas con filtros opcionales (usa conversaciones)."""
    try:
        tipo = request.args.get('tipo')  # 'whatsapp' o 'email'
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 50), 'limit')
        
        conversaciones = conversacion_service.listar_conversaciones(
            db.session,
            tipo_mensaje=tipo,
            skip=skip,
            limit=limit
        )
        
        # Formatear como notificaciones para compatibilidad
        notificaciones = []
        for conv in conversaciones:
            notificaciones.append({
                'tipo': conv.tipo_mensaje.value if conv.tipo_mensaje else None,
                'destinatario': conv.contacto.email if conv.tipo_mensaje == TipoMensajeContacto.EMAIL else conv.contacto.whatsapp,
                'mensaje': conv.contenido,
                'asunto': conv.asunto,
                'fecha': conv.fecha_envio.isoformat() if conv.fecha_envio else None,
                'estado': conv.estado
            })
        
        return paginated_response({'notificaciones': notificaciones}, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/enviar', methods=['POST'])
def enviar_notificacion():
    """Envía una notificación (WhatsApp o Email) a un contacto."""
    try:
        datos = request.get_json()
        if not datos:
            return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
        
        contacto_id = datos.get('contacto_id')
        tipo = datos.get('tipo')
        mensaje = datos.get('mensaje')
        asunto = datos.get('asunto', '')
        
        if not contacto_id:
            return error_response('contacto_id es requerido', 400, 'VALIDATION_ERROR')
        
        if not tipo or not mensaje:
            return error_response('tipo y mensaje son requeridos', 400, 'VALIDATION_ERROR')
        
        # Obtener contacto
        contacto = contacto_service.obtener_contacto(db.session, contacto_id)
        if not contacto:
            return error_response('Contacto no encontrado', 404, 'NOT_FOUND')
        
        mensaje_id_externo = None
        estado = 'enviado'
        error_msg = None
        
        try:
            if tipo == 'whatsapp':
                if not contacto.whatsapp:
                    return error_response('El contacto no tiene WhatsApp configurado', 400, 'VALIDATION_ERROR')
                
                # Limpiar número
                import re
                numero_limpio = re.sub(r'[^0-9]', '', contacto.whatsapp)
                resultado = whatsapp_service.enviar_mensaje(numero_limpio, mensaje)
                
                # WhatsApp API retorna: {"messages": [{"id": "wamid.xxx"}]}
                if isinstance(resultado, dict):
                    messages = resultado.get('messages', [])
                    if messages and len(messages) > 0:
                        mensaje_id_externo = messages[0].get('id')
                        estado = 'enviado'
            
            elif tipo == 'email':
                if not contacto.email:
                    return error_response('El contacto no tiene email configurado', 400, 'VALIDATION_ERROR')
                
                # Convertir mensaje a HTML básico
                contenido_html = f"<p>{mensaje.replace(chr(10), '<br>')}</p>"
                resultado = email_service.enviar_email(
                    contacto.email,
                    asunto or 'Notificación del Sistema',
                    contenido_html,
                    contenido_texto=mensaje
                )
                
                # Email service retorna dict con status_code
                if isinstance(resultado, dict):
                    if resultado.get('status_code') == 200:
                        estado = 'enviado'
                    else:
                        estado = 'error'
                        error_msg = resultado.get('mensaje', 'Error desconocido')
            
            else:
                return error_response('Tipo de notificación no válido. Use "whatsapp" o "email"', 400, 'VALIDATION_ERROR')
            
            # Guardar conversación en historial
            conversacion = conversacion_service.crear_conversacion(
                db.session,
                contacto_id=contacto_id,
                tipo_mensaje=tipo,
                contenido=mensaje,
                asunto=asunto if tipo == 'email' else None,
                mensaje_id_externo=mensaje_id_externo,
                estado=estado,
                error=error_msg
            )
            db.session.commit()
            
            return success_response({
                'conversacion': conversacion.to_dict(),
                'tipo': tipo,
                'mensaje_id': mensaje_id_externo
            }, message=f'Notificación {tipo} enviada correctamente')
            
        except Exception as e:
            # Guardar conversación con error
            try:
                conversacion = conversacion_service.crear_conversacion(
                    db.session,
                    contacto_id=contacto_id,
                    tipo_mensaje=tipo,
                    contenido=mensaje,
                    asunto=asunto if tipo == 'email' else None,
                    estado='error',
                    error=str(e)
                )
                db.session.commit()
            except:
                pass
            
            return error_response(f'Error al enviar notificación: {str(e)}', 500, 'SEND_ERROR')
            
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """Obtiene estadísticas de notificaciones."""
    try:
        estadisticas = conversacion_service.obtener_resumen_conversaciones(db.session)
        return success_response(estadisticas)
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/conversaciones', methods=['GET'])
def listar_conversaciones():
    """Lista conversaciones con filtros opcionales."""
    try:
        contacto_id = request.args.get('contacto_id', type=int)
        tipo_mensaje = request.args.get('tipo_mensaje')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if contacto_id:
            validate_positive_int(contacto_id, 'contacto_id')
        
        conversaciones = conversacion_service.listar_conversaciones(
            db.session,
            contacto_id=contacto_id,
            tipo_mensaje=tipo_mensaje,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([c.to_dict() for c in conversaciones], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/notificaciones/conversaciones/<int:conversacion_id>', methods=['GET'])
def obtener_conversacion(conversacion_id):
    """Obtiene una conversación por ID."""
    try:
        validate_positive_int(conversacion_id, 'conversacion_id')
        conversacion = conversacion_service.obtener_conversacion(db.session, conversacion_id)
        if not conversacion:
            return error_response('Conversación no encontrada', 404, 'NOT_FOUND')
        
        return success_response(conversacion.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
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
        
        # Serializar tickets con manejo de errores
        tickets_dict = []
        for t in tickets:
            try:
                tickets_dict.append(t.to_dict())
            except Exception as e:
                import logging
                logging.error(f"Error serializando ticket {t.id}: {str(e)}")
                # Continuar con el siguiente ticket
                continue
        
        return paginated_response(tickets_dict, skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        import traceback
        import logging
        logging.error(f"Error en listar_tickets: {str(e)}")
        logging.error(traceback.format_exc())
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

# ========== RUTAS DE CONTACTOS ==========

@bp.route('/contactos', methods=['GET'])
def listar_contactos():
    """Lista contactos con filtros opcionales."""
    try:
        tipo = request.args.get('tipo')
        proveedor_id = request.args.get('proveedor_id', type=int)
        proyecto = request.args.get('proyecto')
        activo = request.args.get('activo')
        busqueda = request.args.get('busqueda')
        skip = validate_positive_int(request.args.get('skip', 0), 'skip')
        limit = validate_positive_int(request.args.get('limit', 100), 'limit')
        
        if proveedor_id:
            validate_positive_int(proveedor_id, 'proveedor_id')
        
        activo_bool = None if activo is None else activo.lower() == 'true'
        
        contactos = contacto_service.listar_contactos(
            db.session,
            tipo=tipo,
            proveedor_id=proveedor_id,
            proyecto=proyecto,
            activo=activo_bool,
            busqueda=busqueda,
            skip=skip,
            limit=limit
        )
        
        return paginated_response([c.to_dict() for c in contactos], skip=skip, limit=limit)
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/contactos', methods=['POST'])
@handle_db_transaction
def crear_contacto():
    """Crea un nuevo contacto."""
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    nombre = require_field(datos, 'nombre', 'nombre')
    
    contacto = contacto_service.crear_contacto(
        db.session,
        nombre=nombre,
        email=datos.get('email'),
        whatsapp=datos.get('whatsapp'),
        telefono=datos.get('telefono'),
        proyecto=datos.get('proyecto'),
        cargo=datos.get('cargo'),
        tipo=datos.get('tipo', 'proveedor'),
        proveedor_id=datos.get('proveedor_id'),
        notas=datos.get('notas')
    )
    db.session.commit()
    
    return success_response(contacto.to_dict(), 201, 'Contacto creado correctamente')

@bp.route('/contactos/<int:contacto_id>', methods=['GET'])
def obtener_contacto(contacto_id):
    """Obtiene un contacto por ID."""
    try:
        validate_positive_int(contacto_id, 'contacto_id')
        contacto = contacto_service.obtener_contacto(db.session, contacto_id)
        if not contacto:
            return error_response('Contacto no encontrado', 404, 'NOT_FOUND')
        
        return success_response(contacto.to_dict())
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/contactos/<int:contacto_id>', methods=['PUT'])
@handle_db_transaction
def actualizar_contacto(contacto_id):
    """Actualiza un contacto existente."""
    validate_positive_int(contacto_id, 'contacto_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    try:
        contacto = contacto_service.actualizar_contacto(
            db.session,
            contacto_id,
            nombre=datos.get('nombre'),
            email=datos.get('email'),
            whatsapp=datos.get('whatsapp'),
            telefono=datos.get('telefono'),
            proyecto=datos.get('proyecto'),
            cargo=datos.get('cargo'),
            tipo=datos.get('tipo'),
            proveedor_id=datos.get('proveedor_id'),
            notas=datos.get('notas'),
            activo=datos.get('activo')
        )
        db.session.commit()
        
        return success_response(contacto.to_dict(), message='Contacto actualizado correctamente')
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/contactos/<int:contacto_id>', methods=['DELETE'])
@handle_db_transaction
def eliminar_contacto(contacto_id):
    """Elimina (marca como inactivo) un contacto."""
    validate_positive_int(contacto_id, 'contacto_id')
    eliminado = contacto_service.eliminar_contacto(db.session, contacto_id)
    if not eliminado:
        return error_response('Contacto no encontrado', 404, 'NOT_FOUND')
    
    db.session.commit()
    return success_response(None, message='Contacto eliminado correctamente')

@bp.route('/contactos/<int:contacto_id>/email', methods=['POST'])
def enviar_email_contacto(contacto_id):
    """Envía un email a un contacto."""
    validate_positive_int(contacto_id, 'contacto_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    asunto = require_field(datos, 'asunto', 'asunto')
    contenido = require_field(datos, 'contenido', 'contenido')
    
    try:
        resultado = contacto_service.enviar_mensaje_email(
            db.session,
            contacto_id,
            asunto,
            contenido
        )
        
        if resultado.get('exito'):
            return success_response(resultado, message='Email enviado correctamente')
        else:
            return error_response(resultado.get('mensaje', 'Error al enviar email'), 400, 'SEND_ERROR')
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')

@bp.route('/contactos/<int:contacto_id>/whatsapp', methods=['POST'])
def enviar_whatsapp_contacto(contacto_id):
    """Envía un mensaje de WhatsApp a un contacto."""
    validate_positive_int(contacto_id, 'contacto_id')
    datos = request.get_json()
    if not datos:
        return error_response('Datos JSON requeridos', 400, 'VALIDATION_ERROR')
    
    mensaje = require_field(datos, 'mensaje', 'mensaje')
    
    try:
        resultado = contacto_service.enviar_mensaje_whatsapp(
            db.session,
            contacto_id,
            mensaje
        )
        
        if resultado.get('exito'):
            return success_response(resultado, message='Mensaje de WhatsApp enviado correctamente')
        else:
            return error_response(resultado.get('mensaje', 'Error al enviar WhatsApp'), 400, 'SEND_ERROR')
    except ValueError as e:
        return error_response(str(e), 400, 'VALIDATION_ERROR')
    except Exception as e:
        return error_response(str(e), 500, 'INTERNAL_ERROR')
