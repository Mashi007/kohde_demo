"""
L?gica de negocio para ingreso de facturas con OCR.
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from PIL import Image

from models import Factura, FacturaItem, Proveedor, Item, Inventario
# Cliente removido (m?dulo eliminado)
from models.factura import TipoFactura, EstadoFactura
from utils.ocr import ocr_processor
from utils.helpers import calcular_iva, calcular_total
from config import Config
from modules.crm.notificaciones.whatsapp import whatsapp_service

class FacturaService:
    """Servicio para gesti?n de facturas."""
    
    @staticmethod
    def procesar_factura_desde_imagen(
        db: Session,
        imagen_path: str,
        tipo: str = 'proveedor'
    ) -> Factura:
        """
        Procesa una factura desde una imagen usando OCR.
        
        Args:
            db: Sesi?n de base de datos
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
            raise ValueError("Ya existe una factura con este n?mero")
        
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
            # Intentar encontrar item en base de datos por descripci?n
            item = FacturaService._buscar_item_por_descripcion(db, item_data.get('descripcion', ''))
            
            # Extraer unidad de la descripci?n o usar la del item si existe
            unidad_factura = item_data.get('unidad') or (item.unidad if item else None)
            
            factura_item = FacturaItem(
                factura_id=factura.id,
                item_id=item.id if item else None,
                cantidad_facturada=float(item_data.get('cantidad', 0)),
                precio_unitario=float(item_data.get('precio', 0)),
                subtotal=float(item_data.get('total', 0)),
                unidad=unidad_factura,
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
            # Error no cr?tico, continuar sin notificaci?n
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error al enviar notificaci?n WhatsApp: {e}", exc_info=True)
        
        return factura
    
    @staticmethod
    def aprobar_factura(
        db: Session,
        factura_id: int,
        items_aprobados: List[Dict],
        usuario_id: int,
        aprobar_parcial: bool = False,
        observaciones: str = None
    ) -> Factura:
        """
        Aprueba una factura y actualiza inventario.
        
        Args:
            db: Sesi?n de base de datos
            factura_id: ID de la factura
            items_aprobados: Lista con cantidad_aprobada por cada item
            usuario_id: ID del usuario que aprueba
            aprobar_parcial: Si True, permite aprobaci?n parcial
            
        Returns:
            Factura aprobada
        """
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise ValueError("Factura no encontrada")
        
        if factura.estado == EstadoFactura.APROBADA:
            raise ValueError("La factura ya est? aprobada")
        
        # Actualizar cantidad aprobada en cada item
        todos_aprobados = True
        total_aprobado = 0
        total_facturado = 0
        
        for item_factura in factura.items:
            total_facturado += float(item_factura.cantidad_facturada)
            
            item_aprobado = next(
                (i for i in items_aprobados if i['factura_item_id'] == item_factura.id),
                None
            )
            
            if item_aprobado:
                cantidad_aprobada = float(item_aprobado['cantidad_aprobada'])
                item_factura.cantidad_aprobada = cantidad_aprobada
                
                # Actualizar unidad si se proporciona en la aprobaci?n
                if 'unidad' in item_aprobado and item_aprobado['unidad']:
                    item_factura.unidad = item_aprobado['unidad']
                # Si no tiene unidad y tiene item asociado, usar la del item
                elif not item_factura.unidad and item_factura.item_id:
                    item = db.query(Item).filter(Item.id == item_factura.item_id).first()
                    if item:
                        item_factura.unidad = item.unidad
                
                total_aprobado += cantidad_aprobada
                
                # Si la cantidad aprobada es menor a la facturada, es parcial
                if cantidad_aprobada < float(item_factura.cantidad_facturada):
                    todos_aprobados = False
            else:
                # Si no se proporciona cantidad aprobada, usar la facturada
                item_factura.cantidad_aprobada = float(item_factura.cantidad_facturada)
                # Asegurar que tenga unidad (usar la del item si existe)
                if not item_factura.unidad and item_factura.item_id:
                    item = db.query(Item).filter(Item.id == item_factura.item_id).first()
                    if item:
                        item_factura.unidad = item.unidad
                total_aprobado += float(item_factura.cantidad_facturada)
        
        # Verificar si se aprob? el 100%
        porcentaje_aprobado = (total_aprobado / total_facturado * 100) if total_facturado > 0 else 0
        
        # Actualizar estado de factura
        if todos_aprobados and porcentaje_aprobado >= 100:
            factura.estado = EstadoFactura.APROBADA
        elif porcentaje_aprobado > 0:
            factura.estado = EstadoFactura.PARCIAL
        else:
            raise ValueError("Debe aprobar al menos un item")
        
        factura.aprobado_por = usuario_id
        factura.fecha_aprobacion = datetime.utcnow()
        if observaciones:
            factura.observaciones = observaciones
        
        # Actualizar inventario solo con items aprobados
        # IMPORTANTE: Las cantidades se deben convertir a la unidad est?ndar del item antes de actualizar inventario
        from modules.logistica.conversor_unidades import son_unidades_compatibles, convertir_unidad
        
        for item_factura in factura.items:
            if item_factura.cantidad_aprobada and item_factura.cantidad_aprobada > 0 and item_factura.item_id:
                item = db.query(Item).filter(Item.id == item_factura.item_id).first()
                if item:
                    # Obtener unidad de la factura
                    unidad_factura = item_factura.unidad if item_factura.unidad else item.unidad
                    cantidad_aprobada = float(item_factura.cantidad_aprobada)
                    unidad_estandar = item.unidad  # Unidad est?ndar del m?dulo Items
                    
                    # Convertir a unidad est?ndar si es necesario
                    if son_unidades_compatibles(unidad_factura, unidad_estandar) and unidad_factura != unidad_estandar:
                        cantidad_estandarizada = convertir_unidad(cantidad_aprobada, unidad_factura, unidad_estandar)
                        if cantidad_estandarizada:
                            cantidad_aprobada = cantidad_estandarizada
                    
                    # Actualizar inventario con cantidad estandarizada
                    FacturaService._actualizar_inventario(
                        db,
                        item_factura.item_id,
                        cantidad_aprobada,
                        float(item_factura.precio_unitario)
                    )
        
        db.commit()
        db.refresh(factura)
        return factura
    
    @staticmethod
    def rechazar_factura(
        db: Session,
        factura_id: int,
        usuario_id: int,
        motivo: str
    ) -> Factura:
        """
        Rechaza una factura.
        
        Args:
            db: Sesi?n de base de datos
            factura_id: ID de la factura
            usuario_id: ID del usuario que rechaza
            motivo: Motivo del rechazo
            
        Returns:
            Factura rechazada
        """
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise ValueError("Factura no encontrada")
        
        if factura.estado == EstadoFactura.APROBADA:
            raise ValueError("No se puede rechazar una factura aprobada")
        
        factura.estado = EstadoFactura.RECHAZADA
        factura.observaciones = motivo
        factura.aprobado_por = usuario_id
        factura.fecha_aprobacion = datetime.utcnow()
        
        db.commit()
        db.refresh(factura)
        return factura
    
    @staticmethod
    def enviar_a_revision(
        db: Session,
        factura_id: int,
        usuario_id: int,
        observaciones: str
    ) -> Factura:
        """
        Env?a una factura a revisi?n (mantiene estado PENDIENTE pero con observaciones).
        
        Args:
            db: Sesi?n de base de datos
            factura_id: ID de la factura
            usuario_id: ID del usuario que env?a a revisi?n
            observaciones: Observaciones sobre qu? necesita revisi?n
            
        Returns:
            Factura en revisi?n
        """
        factura = db.query(Factura).filter(Factura.id == factura_id).first()
        if not factura:
            raise ValueError("Factura no encontrada")
        
        if factura.estado != EstadoFactura.PENDIENTE:
            raise ValueError("Solo se pueden enviar a revisi?n facturas pendientes")
        
        factura.observaciones = observaciones
        # Mantener estado PENDIENTE para que pueda ser reprocesada
        
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
    
    # M?todo _buscar_o_crear_cliente removido (m?dulo Cliente eliminado)
    
    @staticmethod
    def _buscar_item_por_descripcion(db: Session, descripcion: str) -> Optional[Item]:
        """Busca un item por descripci?n (b?squeda aproximada)."""
        # B?squeda simple por nombre similar
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
