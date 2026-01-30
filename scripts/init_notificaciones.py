"""
Script para generar datos mock de notificaciones basadas en reglas del negocio.
Las notificaciones son conversaciones con contactos (proveedores/colaboradores) por email o WhatsApp.
"""
import sys
import os
from datetime import datetime, timedelta
from random import choice, randint, uniform

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.conversacion_contacto import ConversacionContacto, TipoMensajeContacto, DireccionMensaje
from models.contacto import Contacto, TipoContacto
from models.inventario import Inventario
from models.item import Item
from models.proveedor import Proveedor
from models.factura import Factura, EstadoFactura, TipoFactura
from models.pedido import PedidoCompra, EstadoPedido

def generar_notificaciones_mock():
    """Genera notificaciones mock basadas en reglas del negocio."""
    print("=" * 70)
    print("GENERACIÓN DE NOTIFICACIONES MOCK")
    print("=" * 70)
    print()
    
    # Obtener contactos existentes
    contactos = db.session.query(Contacto).filter(Contacto.activo == True).all()
    if not contactos:
        print("⚠️  No hay contactos activos. Creando contactos de ejemplo...")
        contactos = crear_contactos_ejemplo()
    
    proveedores = db.session.query(Proveedor).limit(5).all()
    items = db.session.query(Item).filter(Item.activo == True).limit(10).all()
    
    notificaciones_creadas = []
    
    # 1. NOTIFICACIONES DE INVENTARIO BAJO MÍNIMO (Urgente - WhatsApp)
    print("\n1️⃣ Generando notificaciones de inventario bajo mínimo...")
    inventarios_bajos = db.session.query(Inventario).filter(
        Inventario.cantidad_actual < Inventario.cantidad_minima
    ).limit(5).all()
    
    for inv in inventarios_bajos:
        contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.whatsapp])
        if not contacto:
            continue
        
        item = inv.item
        porcentaje = (float(inv.cantidad_actual) / float(inv.cantidad_minima) * 100) if inv.cantidad_minima > 0 else 0
        
        contenido = f"⚠️ ALERTA DE INVENTARIO\n\n"
        contenido += f"El item '{item.nombre}' está por debajo del mínimo.\n"
        contenido += f"Stock actual: {inv.cantidad_actual:.2f} {inv.unidad}\n"
        contenido += f"Stock mínimo: {inv.cantidad_minima:.2f} {inv.unidad}\n"
        contenido += f"Porcentaje: {porcentaje:.1f}%\n\n"
        contenido += f"Por favor, considere realizar un pedido urgente."
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='whatsapp',
            contenido=contenido,
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ WhatsApp a {contacto.nombre}: Inventario bajo - {item.nombre}")
    
    # 2. NOTIFICACIONES DE FACTURAS PENDIENTES (Media - Email)
    print("\n2️⃣ Generando notificaciones de facturas pendientes...")
    facturas_pendientes = db.session.query(Factura).filter(
        Factura.estado == EstadoFactura.PENDIENTE,
        Factura.tipo == TipoFactura.PROVEEDOR
    ).limit(3).all()
    
    for factura in facturas_pendientes:
        contacto = None
        if factura.proveedor_id:
            contacto = next((c for c in contactos if c.proveedor_id == factura.proveedor_id and c.email), None)
        
        if not contacto:
            contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.email])
        
        if not contacto:
            continue
        
        contenido = f"Estimado/a {contacto.nombre},\n\n"
        contenido += f"Le recordamos que tiene una factura pendiente de revisión:\n\n"
        contenido += f"• Número de factura: {factura.numero_factura}\n"
        contenido += f"• Fecha de recepción: {factura.fecha_recepcion.strftime('%d/%m/%Y')}\n"
        contenido += f"• Total: ${factura.total:.2f}\n\n"
        contenido += f"Por favor, revise y apruebe la factura en el sistema cuando sea posible.\n\n"
        contenido += f"Saludos cordiales,\nEquipo de Logística"
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='email',
            contenido=contenido,
            asunto=f"Recordatorio: Factura {factura.numero_factura} pendiente",
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ Email a {contacto.nombre}: Factura pendiente - {factura.numero_factura}")
    
    # 3. NOTIFICACIONES DE PEDIDOS AUTOMÁTICOS (Alta - Email)
    print("\n3️⃣ Generando notificaciones de pedidos automáticos...")
    pedidos_pendientes = db.session.query(PedidoCompra).filter(
        PedidoCompra.estado == EstadoPedido.PENDIENTE
    ).limit(3).all()
    
    for pedido in pedidos_pendientes:
        contacto = None
        if pedido.proveedor_id:
            contacto = next((c for c in contactos if c.proveedor_id == pedido.proveedor_id and c.email), None)
        
        if not contacto:
            contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.email])
        
        if not contacto:
            continue
        
        total_items = len(pedido.items) if hasattr(pedido, 'items') else 0
        
        contenido = f"Estimado/a {contacto.nombre},\n\n"
        contenido += f"Se ha generado un pedido automático basado en los requerimientos del sistema:\n\n"
        contenido += f"• Número de pedido: #{pedido.id}\n"
        contenido += f"• Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y')}\n"
        contenido += f"• Total de items: {total_items}\n"
        contenido += f"• Estado: Pendiente de aprobación\n\n"
        contenido += f"Por favor, revise el pedido en el sistema y apruebe cuando esté listo para enviar.\n\n"
        contenido += f"Saludos cordiales,\nSistema de Gestión"
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='email',
            contenido=contenido,
            asunto=f"Pedido automático #{pedido.id} generado",
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ Email a {contacto.nombre}: Pedido automático - #{pedido.id}")
    
    # 4. NOTIFICACIONES DE STOCK CRÍTICO (Urgente - WhatsApp)
    print("\n4️⃣ Generando notificaciones de stock crítico...")
    inventarios_criticos = db.session.query(Inventario).filter(
        Inventario.cantidad_actual < (Inventario.cantidad_minima * 0.5)
    ).limit(3).all()
    
    for inv in inventarios_criticos:
        contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.whatsapp])
        if not contacto:
            continue
        
        item = inv.item
        
        contenido = f"🚨 STOCK CRÍTICO\n\n"
        contenido += f"El item '{item.nombre}' está en nivel crítico.\n"
        contenido += f"Stock actual: {inv.cantidad_actual:.2f} {inv.unidad}\n"
        contenido += f"Stock mínimo: {inv.cantidad_minima:.2f} {inv.unidad}\n\n"
        contenido += f"Se requiere atención inmediata. Por favor, contacte al área de compras."
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='whatsapp',
            contenido=contenido,
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ WhatsApp a {contacto.nombre}: Stock crítico - {item.nombre}")
    
    # 5. NOTIFICACIONES DE CONFIRMACIÓN DE ENTREGA (Media - Email)
    print("\n5️⃣ Generando notificaciones de confirmación de entrega...")
    facturas_aprobadas_recientes = db.session.query(Factura).filter(
        Factura.estado == EstadoFactura.APROBADA,
        Factura.tipo == TipoFactura.PROVEEDOR,
        Factura.fecha_aprobacion >= datetime.now() - timedelta(days=2)
    ).limit(2).all()
    
    for factura in facturas_aprobadas_recientes:
        contacto = None
        if factura.proveedor_id:
            contacto = next((c for c in contactos if c.proveedor_id == factura.proveedor_id and c.email), None)
        
        if not contacto:
            contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.email])
        
        if not contacto:
            continue
        
        contenido = f"Estimado/a {contacto.nombre},\n\n"
        contenido += f"Le confirmamos que la factura ha sido aprobada y el inventario ha sido actualizado:\n\n"
        contenido += f"• Número de factura: {factura.numero_factura}\n"
        contenido += f"• Fecha de aprobación: {factura.fecha_aprobacion.strftime('%d/%m/%Y %H:%M')}\n"
        contenido += f"• Total: ${factura.total:.2f}\n\n"
        contenido += f"Gracias por su colaboración.\n\n"
        contenido += f"Saludos cordiales,\nEquipo de Logística"
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='email',
            contenido=contenido,
            asunto=f"Confirmación: Factura {factura.numero_factura} aprobada",
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ Email a {contacto.nombre}: Confirmación factura - {factura.numero_factura}")
    
    # 6. NOTIFICACIONES DE RECORDATORIO DE PEDIDOS (Media - Email)
    print("\n6️⃣ Generando notificaciones de recordatorio de pedidos...")
    pedidos_enviados = db.session.query(PedidoCompra).filter(
        PedidoCompra.estado == EstadoPedido.ENVIADO,
        PedidoCompra.fecha_envio >= datetime.now() - timedelta(days=3)
    ).limit(2).all()
    
    for pedido in pedidos_enviados:
        contacto = None
        if pedido.proveedor_id:
            contacto = next((c for c in contactos if c.proveedor_id == pedido.proveedor_id and c.email), None)
        
        if not contacto:
            contacto = choice([c for c in contactos if c.tipo == TipoContacto.PROVEEDOR and c.email])
        
        if not contacto:
            continue
        
        dias_desde_envio = (datetime.now() - pedido.fecha_envio).days
        
        contenido = f"Estimado/a {contacto.nombre},\n\n"
        contenido += f"Le recordamos que el pedido #{pedido.id} fue enviado hace {dias_desde_envio} día(s).\n\n"
        contenido += f"• Número de pedido: #{pedido.id}\n"
        contenido += f"• Fecha de envío: {pedido.fecha_envio.strftime('%d/%m/%Y')}\n"
        contenido += f"• Estado: Enviado\n\n"
        contenido += f"Por favor, confirme la recepción del pedido cuando sea posible.\n\n"
        contenido += f"Saludos cordiales,\nEquipo de Compras"
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='email',
            contenido=contenido,
            asunto=f"Recordatorio: Pedido #{pedido.id} enviado",
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ Email a {contacto.nombre}: Recordatorio pedido - #{pedido.id}")
    
    # 7. NOTIFICACIONES DE BIENVENIDA (Baja - Email)
    print("\n7️⃣ Generando notificaciones de bienvenida...")
    contactos_nuevos = db.session.query(Contacto).filter(
        Contacto.fecha_registro >= datetime.now() - timedelta(days=7),
        Contacto.email.isnot(None)
    ).limit(2).all()
    
    for contacto in contactos_nuevos:
        contenido = f"Estimado/a {contacto.nombre},\n\n"
        contenido += f"Bienvenido/a al sistema de gestión de restaurantes.\n\n"
        contenido += f"Su cuenta ha sido creada exitosamente y podrá recibir notificaciones sobre:\n"
        contenido += f"• Pedidos y facturas\n"
        contenido += f"• Alertas de inventario\n"
        contenido += f"• Confirmaciones de entrega\n\n"
        contenido += f"Si tiene alguna pregunta, no dude en contactarnos.\n\n"
        contenido += f"Saludos cordiales,\nEquipo de Soporte"
        
        notif = crear_notificacion(
            contacto_id=contacto.id,
            tipo='email',
            contenido=contenido,
            asunto="Bienvenido al Sistema de Gestión",
            estado='enviado'
        )
        notificaciones_creadas.append(notif)
        print(f"  ✓ Email a {contacto.nombre}: Bienvenida")
    
    # Guardar todas las notificaciones
    db.session.commit()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE NOTIFICACIONES GENERADAS")
    print("=" * 70)
    print(f"✅ Total notificaciones creadas: {len(notificaciones_creadas)}")
    
    # Estadísticas por tipo
    email_count = sum(1 for n in notificaciones_creadas if n.tipo_mensaje == TipoMensajeContacto.EMAIL)
    whatsapp_count = sum(1 for n in notificaciones_creadas if n.tipo_mensaje == TipoMensajeContacto.WHATSAPP)
    
    print(f"   • Email: {email_count}")
    print(f"   • WhatsApp: {whatsapp_count}")
    
    print("\n✅ Notificaciones mock generadas exitosamente!")
    print("💡 Puedes verlas en: /notificaciones")
    
    return notificaciones_creadas

def crear_notificacion(contacto_id, tipo, contenido, asunto=None, estado='enviado', fecha_envio=None):
    """Crea una notificación (conversación) en la base de datos."""
    if fecha_envio is None:
        # Generar fechas aleatorias en los últimos 7 días
        fecha_envio = datetime.now() - timedelta(days=randint(0, 7), hours=randint(0, 23))
    
    tipo_enum = TipoMensajeContacto[tipo.upper()]
    
    notificacion = ConversacionContacto(
        contacto_id=contacto_id,
        tipo_mensaje=tipo_enum,
        direccion=DireccionMensaje.ENVIADO,
        asunto=asunto,
        contenido=contenido,
        estado=estado,
        fecha_envio=fecha_envio,
        fecha_creacion=fecha_envio
    )
    
    db.session.add(notificacion)
    return notificacion

def crear_contactos_ejemplo():
    """Crea contactos de ejemplo si no existen."""
    proveedores = db.session.query(Proveedor).limit(3).all()
    contactos_creados = []
    
    nombres_ejemplo = [
        ("Juan Pérez", "juan.perez@proveedor.com", "+521234567890"),
        ("María González", "maria.gonzalez@proveedor.com", "+521234567891"),
        ("Carlos Rodríguez", "carlos.rodriguez@proveedor.com", "+521234567892"),
    ]
    
    for i, (nombre, email, whatsapp) in enumerate(nombres_ejemplo):
        proveedor_id = proveedores[i].id if i < len(proveedores) else None
        
        contacto = Contacto(
            nombre=nombre,
            email=email,
            whatsapp=whatsapp,
            tipo=TipoContacto.PROVEEDOR,
            proveedor_id=proveedor_id,
            activo=True
        )
        
        db.session.add(contacto)
        contactos_creados.append(contacto)
    
    db.session.commit()
    return contactos_creados

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            notificaciones = generar_notificaciones_mock()
            print(f"\n✅ Proceso completado exitosamente!")
            print(f"📧 Total: {len(notificaciones)} notificaciones generadas")
        except Exception as e:
            import traceback
            print(f"\n❌ Error: {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()
