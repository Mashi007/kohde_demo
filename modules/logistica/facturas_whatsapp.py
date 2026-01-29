"""
Servicio para procesar facturas recibidas por WhatsApp.
Incluye descarga de imagen, OCR, identificación de proveedor y creación de factura pendiente.
"""
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import requests
import os
from pathlib import Path
from models import Factura, FacturaItem, Proveedor, Item
from models.factura import TipoFactura, EstadoFactura
from utils.ocr import ocr_processor
from config import Config

class FacturasWhatsAppService:
    """Servicio para procesar facturas desde WhatsApp."""
    
    @staticmethod
    def descargar_imagen_whatsapp(image_id: str, access_token: str) -> Optional[str]:
        """
        Descarga una imagen desde WhatsApp Business API.
        
        Args:
            image_id: ID de la imagen en WhatsApp
            access_token: Token de acceso de WhatsApp
            
        Returns:
            Ruta del archivo descargado o None
        """
        try:
            # Obtener URL de la imagen desde WhatsApp API
            whatsapp_api_url = Config.WHATSAPP_API_URL or 'https://graph.facebook.com/v18.0'
            phone_number_id = Config.WHATSAPP_PHONE_NUMBER_ID
            
            if not phone_number_id:
                print("Error: WHATSAPP_PHONE_NUMBER_ID no configurado")
                return None
            
            # URL para obtener la imagen: /{phone-number-id}/media/{media-id}
            url = f"{whatsapp_api_url}/{phone_number_id}/media/{image_id}"
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            image_data = response.json()
            image_url = image_data.get('url')
            
            if not image_url:
                return None
            
            # Descargar la imagen
            image_response = requests.get(image_url, headers=headers)
            image_response.raise_for_status()
            
            # Guardar imagen
            upload_dir = Path(Config.UPLOAD_FOLDER)
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"factura_whatsapp_{image_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = upload_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(image_response.content)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Error al descargar imagen de WhatsApp: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def identificar_proveedor_por_ruc(db: Session, ruc: str) -> Optional[Proveedor]:
        """
        Identifica un proveedor por su RUC.
        
        Args:
            db: Sesión de base de datos
            ruc: Número de RUC del proveedor
            
        Returns:
            Proveedor encontrado o None
        """
        if not ruc:
            return None
        
        # Buscar proveedor por RUC
        proveedor = db.query(Proveedor).filter(Proveedor.ruc == ruc).first()
        return proveedor
    
    @staticmethod
    def procesar_factura_desde_whatsapp(
        db: Session,
        image_id: str,
        sender_id: str,
        sender_name: str = None
    ) -> Dict:
        """
        Procesa una factura recibida por WhatsApp.
        
        Args:
            db: Sesión de base de datos
            image_id: ID de la imagen en WhatsApp
            sender_id: ID del remitente (teléfono)
            sender_name: Nombre del remitente (opcional)
            
        Returns:
            Diccionario con resultado del procesamiento
        """
        try:
            # Descargar imagen
            access_token = Config.WHATSAPP_ACCESS_TOKEN
            if not access_token:
                return {
                    'exito': False,
                    'mensaje': 'Token de WhatsApp no configurado'
                }
            
            image_path = FacturasWhatsAppService.descargar_imagen_whatsapp(image_id, access_token)
            if not image_path:
                return {
                    'exito': False,
                    'mensaje': 'Error al descargar imagen de WhatsApp'
                }
            
            # Procesar con OCR
            datos_ocr = ocr_processor.extract_invoice_data(image_path)
            
            if not datos_ocr.get('numero_factura'):
                return {
                    'exito': False,
                    'mensaje': 'No se pudo extraer información de la factura. Verifica que la imagen sea clara.'
                }
            
            # Identificar proveedor por RUC
            proveedor = None
            if datos_ocr.get('ruc'):
                proveedor = FacturasWhatsAppService.identificar_proveedor_por_ruc(
                    db, datos_ocr['ruc']
                )
            
            # Crear factura pendiente
            factura = Factura(
                numero_factura=datos_ocr.get('numero_factura', f'FAC-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
                tipo=TipoFactura.PROVEEDOR,
                proveedor_id=proveedor.id if proveedor else None,
                fecha_emision=FacturasWhatsAppService._parse_fecha(datos_ocr.get('fecha')),
                subtotal=float(datos_ocr.get('subtotal', 0)) or float(datos_ocr.get('total', 0)),
                iva=float(datos_ocr.get('iva', 0)),
                total=float(datos_ocr.get('total', 0)),
                estado=EstadoFactura.PENDIENTE,
                imagen_url=f"/uploads/{Path(image_path).name}",
                items_json=datos_ocr.get('items', []),
                remitente_nombre=sender_name or sender_id,
                remitente_telefono=sender_id,
                recibida_por_whatsapp=True,
                whatsapp_message_id=image_id
            )
            
            db.add(factura)
            db.flush()
            
            # Crear items de factura desde OCR (pendientes de confirmación)
            for item_ocr in datos_ocr.get('items', []):
                # Buscar item por descripción (fuzzy match)
                item = FacturasWhatsAppService._buscar_item_por_descripcion(
                    db, item_ocr.get('descripcion', '')
                )
                
                # Extraer unidad de la descripción o usar la del item si existe
                unidad_factura = item_ocr.get('unidad') or (item.unidad if item else None)
                
                factura_item = FacturaItem(
                    factura_id=factura.id,
                    item_id=item.id if item else None,
                    cantidad_facturada=float(item_ocr.get('cantidad', 0)),
                    cantidad_aprobada=None,  # Se llenará al confirmar
                    precio_unitario=float(item_ocr.get('precio', 0)),
                    subtotal=float(item_ocr.get('total', 0)),
                    unidad=unidad_factura,
                    descripcion=item_ocr.get('descripcion', '')
                )
                db.add(factura_item)
            
            db.commit()
            db.refresh(factura)
            
            return {
                'exito': True,
                'factura_id': factura.id,
                'numero_factura': factura.numero_factura,
                'total': float(factura.total),
                'proveedor': proveedor.nombre if proveedor else datos_ocr.get('proveedor', 'No identificado'),
                'items': len(datos_ocr.get('items', []))
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error al procesar factura desde WhatsApp: {e}")
            import traceback
            traceback.print_exc()
            return {
                'exito': False,
                'mensaje': f'Error al procesar factura: {str(e)}'
            }
    
    @staticmethod
    def _parse_fecha(fecha_str: str) -> datetime:
        """
        Parsea una fecha desde string a datetime.
        
        Args:
            fecha_str: String de fecha en varios formatos
            
        Returns:
            datetime o datetime.now() si no se puede parsear
        """
        if not fecha_str:
            return datetime.now()
        
        try:
            # Intentar varios formatos
            formatos = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y']
            for formato in formatos:
                try:
                    return datetime.strptime(fecha_str, formato)
                except:
                    continue
        except:
            pass
        
        return datetime.now()
    
    @staticmethod
    def _buscar_item_por_descripcion(db: Session, descripcion: str) -> Optional[Item]:
        """
        Busca un item por descripción (fuzzy match).
        
        Args:
            db: Sesión de base de datos
            descripcion: Descripción del item
            
        Returns:
            Item encontrado o None
        """
        if not descripcion:
            return None
        
        # Buscar por nombre similar
        from sqlalchemy import or_
        descripcion_lower = descripcion.lower()
        
        # Buscar items que contengan palabras clave de la descripción
        palabras = descripcion_lower.split()[:3]  # Primeras 3 palabras
        
        query = db.query(Item).filter(Item.activo == True)
        
        condiciones = []
        for palabra in palabras:
            if len(palabra) > 2:  # Solo palabras de más de 2 caracteres
                condiciones.append(Item.nombre.ilike(f'%{palabra}%'))
        
        if condiciones:
            query = query.filter(or_(*condiciones))
            item = query.first()
            return item
        
        return None
