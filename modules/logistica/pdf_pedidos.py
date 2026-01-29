"""
Servicio para generar PDFs de pedidos.
"""
from typing import Optional
from datetime import datetime
from pathlib import Path
from config import Config

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

def generar_pdf_pedido(pedido) -> str:
    """
    Genera un PDF del pedido.
    
    Args:
        pedido: Instancia de PedidoCompra
        
    Returns:
        Ruta del archivo PDF generado
    """
    if not REPORTLAB_AVAILABLE:
        # Si reportlab no está disponible, crear un PDF básico o retornar None
        raise ImportError("reportlab no está instalado. Instala con: pip install reportlab")
    
    # Nombre del archivo
    filename = f"pedido_{pedido.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = PDF_FOLDER / filename
    
    # Crear documento PDF
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    story.append(Paragraph("ORDEN DE COMPRA", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Información del pedido
    proveedor = pedido.proveedor
    info_data = [
        ['Pedido #:', str(pedido.id)],
        ['Fecha:', pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M') if pedido.fecha_pedido else 'N/A'],
        ['Proveedor:', proveedor.nombre if proveedor else 'N/A'],
        ['RUC:', proveedor.ruc if proveedor and proveedor.ruc else 'N/A'],
        ['Contacto:', proveedor.nombre_contacto if proveedor and proveedor.nombre_contacto else 'N/A'],
        ['Teléfono:', proveedor.telefono if proveedor and proveedor.telefono else 'N/A'],
        ['Email:', proveedor.email if proveedor and proveedor.email else 'N/A'],
        ['Fecha Entrega Esperada:', pedido.fecha_entrega_esperada.strftime('%d/%m/%Y') if pedido.fecha_entrega_esperada else 'N/A'],
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 1*cm))
    
    # Tabla de items
    items_data = [['Item', 'Cantidad', 'Unidad', 'Precio Unit.', 'Subtotal']]
    
    for item in pedido.items:
        items_data.append([
            item.item.nombre,
            f"{float(item.cantidad):,.2f}",
            item.item.unidad,
            f"${float(item.precio_unitario):,.2f}",
            f"${float(item.subtotal):,.2f}"
        ])
    
    # Agregar total
    items_data.append([
        '',
        '',
        '',
        Paragraph('<b>TOTAL:</b>', styles['Normal']),
        Paragraph(f'<b>${float(pedido.total):,.2f}</b>', styles['Normal'])
    ])
    
    items_table = Table(items_data, colWidths=[7*cm, 2*cm, 2*cm, 2*cm, 2*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E5E7EB')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(Paragraph("Items del Pedido:", styles['Heading2']))
    story.append(Spacer(1, 0.3*cm))
    story.append(items_table)
    
    # Observaciones
    if pedido.observaciones:
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph(f"<b>Observaciones:</b> {pedido.observaciones}", styles['Normal']))
    
    # Generar PDF
    doc.build(story)
    
    return str(filepath)
