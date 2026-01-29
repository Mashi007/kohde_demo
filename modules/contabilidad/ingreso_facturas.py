"""
Lógica de negocio para ingreso de facturas con OCR.
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from PIL import Image

from models import Factura, FacturaItem, Proveedor, Item, Inventario
# Cliente removido (módulo eliminado)
from models.factura import TipoFactura, EstadoFactura
from utils.ocr import ocr_processor
from utils.helpers import calcular_iva, calcular_total
from config import Config
from modules.notificaciones.whatsapp import whatsapp_service

class FacturaService:
    """Servicio para gestión de facturas."""
    
    @staticmethod
    def procesar_factura_desde_imagen(
        db: Session,
        imagen_path: str,
        tipo: str = 'proveedor'
    ) -> Factura:
        """
        Procesa una factura desde una imagen usando OCR.
        
        Args:
            db: Sesión de base de datos
            imagen_path: Ruta al archivo de imagen
            tipo: Tipo de factura ('cliente' o 'proveedor')
            
        Returns:
            Factura creada
        """
        # 1. Guardar imagen en servidor
        imagen_url = FacturaService._guardar_imagen(imagen_path)
        
        # 2. Extraer datos con OCR
        datos_ocr = ocr_processor.extract_invoice_data(imagen_path)
        
        # 3. Buscar o crear proveedor
        if tipo == 'proveedor':
            proveedor = FacturaService._buscar_o_crear_proveedor(db, datos_ocr)
            cliente_id = None
            proveedor_id = proveedor.id
        else:
            # Cliente removido - facturas de cliente ahora sin proveedor
            proveedor_id = None
            cliente_id = None
        
        # 4. Verificar duplicados
        factura_existente = db.query(Factura).filter(
            Factura.numero_factura == datos_ocr.get('numero_factura')
        ).first()
        
        if factura_existente:
            raise ValueError("Ya existe una factura con este número")
        
        # 5. Crear factura
        fecha_emision = FacturaService._parsear_fecha(datos_ocr.get('fecha'))
        
        factura = Factura(
            numero_factura=datos_ocr.get('numero_factura', 'SIN-NUMERO'),
            tipo=TipoFactura[tipo.upper()],
            cliente_id=cliente_id,
            proveedor_id=proveedor_id,
            fecha_emision=fecha_emision or datetime.utcnow(),
            subtotal=float(datos_ocr.get('subtotal', 0)),
            iva=float(datos_ocr.get('iva', 0)),
            total=float(datos_ocr.get('total', 0)),
            estado=EstadoFactura.PENDIENTE,
            imagen_url=imagen_url,
            items_json=datos_ocr.get('items', [])
        )
        
        db.add(factura)
        
        # 6. Crear items de factura
        for item_data in datos_ocr.get('items', []):
            # Intentar encontrar item en base de datos por descripción
            item = FacturaService._buscar_item_por_descripcion(db, item_data.get('descripcion', ''))
            
            factura_item = FacturaItem(
                factura_id=factura.id,
                item_id=item.id if item else None,
                cantidad_facturada=float(item_data.get('cantidad', 0)),
                precio_unitario=float(item_data.get('precio', 0)),
                subtotal=float(item_data.get('total', 0)),
                descripcion=item_data.get('descripcion', '')
            )
            db.add(factura_item)
        
        db.commit()
        db.refresh(factura)
        
        # 7. Notificar a bodega
        try:
            if tipo == 'proveedor' and proveedor.telefono:
                whatsapp_service.notificar_factura_recibida(
                    proveedor.telefono,
                    {
                        'proveedor': proveedor.nombre,
                        'numero_factura': factura.numero_factura,
                        'total': float(factura.total)
                    }
                )
        except Exception as e:
            print(f"Error al enviar notificación WhatsApp: {e}")
        
        return factura
    
    @staticmethod
    def aprobar_factura(
        db: Session,
        factura_id: int,
        items_aprobados: List[Dict],
        usuario_id: int,
        aprobar_parcial: bool = False
    ) -> Factura:
        """
        Aprueba una factura y actualiza inventario.
        
        Args:
            db: Sesión de base de datos
            factura_id: ID de la factura
            items_aprobados: Lista con cantidad_aprobada por cada item
            usuario_id: ID del usuario que aprueba
            aprobar_parcial: Si True, permite aprobación parcial
            
        Returns:
            Factura aprobada
        """
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise ValueError("Factura no encontrada")
        
        if factura.estado == EstadoFactura.APROBADA:
            raise ValueError("La factura ya está aprobada")
        
        # Actualizar cantidad aprobada en cada item
        todos_aprobados = True
        for item_factura in factura.items:
            item_aprobado = next(
                (i for i in items_aprobados if i['factura_item_id'] == item_factura.id),
                None
            )
            
            if item_aprobado:
                cantidad_aprobada = float(item_aprobado['cantidad_aprobada'])
                item_factura.cantidad_aprobada = cantidad_aprobada
                
                # Si la cantidad aprobada es menor a la facturada, es parcial
                if cantidad_aprobada < float(item_factura.cantidad_facturada):
                    todos_aprobados = False
            else:
                todos_aprobados = False
        
        # Actualizar estado de factura
        if todos_aprobados:
            factura.estado = EstadoFactura.APROBADA
        elif aprobar_parcial:
            factura.estado = EstadoFactura.PARCIAL
        else:
            raise ValueError("No se puede aprobar parcialmente sin el flag aprobar_parcial")
        
        factura.aprobado_por = usuario_id
        factura.fecha_aprobacion = datetime.utcnow()
        
        # Actualizar inventario solo con items aprobados
        for item_factura in factura.items:
            if item_factura.cantidad_aprobada and item_factura.item_id:
                FacturaService._actualizar_inventario(
                    db,
                    item_factura.item_id,
                    float(item_factura.cantidad_aprobada),
                    float(item_factura.precio_unitario)
                )
        
        db.commit()
        db.refresh(factura)
        return factura
    
    @staticmethod
    def _guardar_imagen(imagen_path: str) -> str:
        """Guarda la imagen y retorna la URL."""
        filename = secure_filename(os.path.basename(imagen_path))
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        destino = Config.UPLOAD_FOLDER / new_filename
        
        # Copiar archivo
        import shutil
        shutil.copy(imagen_path, destino)
        
        return f"/uploads/facturas/{new_filename}"
    
    @staticmethod
    def _buscar_o_crear_proveedor(db: Session, datos: Dict) -> Proveedor:
        """Busca o crea un proveedor basado en datos OCR."""
        ruc = datos.get('ruc')
        nombre = datos.get('proveedor', 'Proveedor Desconocido')
        
        if ruc:
            proveedor = db.query(Proveedor).filter(Proveedor.ruc == ruc).first()
            if proveedor:
                return proveedor
        
        # Buscar por nombre
        proveedor = db.query(Proveedor).filter(Proveedor.nombre.ilike(f'%{nombre}%')).first()
        if proveedor:
            return proveedor
        
        # Crear nuevo proveedor
        proveedor = Proveedor(
            nombre=nombre,
            ruc=ruc
        )
        db.add(proveedor)
        db.commit()
        db.refresh(proveedor)
        return proveedor
    
    # Método _buscar_o_crear_cliente removido (módulo Cliente eliminado)
    
    @staticmethod
    def _buscar_item_por_descripcion(db: Session, descripcion: str) -> Optional[Item]:
        """Busca un item por descripción (búsqueda aproximada)."""
        # Búsqueda simple por nombre similar
        items = db.query(Item).filter(Item.nombre.ilike(f'%{descripcion[:20]}%')).all()
        if items:
            return items[0]
        return None
    
    @staticmethod
    def _parsear_fecha(fecha_string: Optional[str]) -> Optional[datetime]:
        """Parsea una fecha desde string."""
        if not fecha_string:
            return None
        
        formatos = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
        for formato in formatos:
            try:
                return datetime.strptime(fecha_string, formato)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def _actualizar_inventario(
        db: Session,
        item_id: int,
        cantidad: float,
        costo_unitario: float
    ):
        """Actualiza el inventario con una entrada."""
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        
        if inventario:
            inventario.cantidad_actual += cantidad
            inventario.ultimo_costo_unitario = costo_unitario
            inventario.ultima_actualizacion = datetime.utcnow()
        else:
            # Crear registro de inventario si no existe
            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                inventario = Inventario(
                    item_id=item_id,
                    cantidad_actual=cantidad,
                    unidad=item.unidad,
                    ultimo_costo_unitario=costo_unitario
                )
                db.add(inventario)
        
        # Actualizar costo unitario del item
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            item.costo_unitario_actual = costo_unitario
        
        db.commit()
