"""
Integración con Google Cloud Vision API para OCR de facturas.
"""
import os
import json
from typing import Dict, List, Optional
from google.cloud import vision
from google.oauth2 import service_account
from config import Config

class OCRProcessor:
    """Procesador de OCR para facturas."""
    
    def __init__(self):
        """Inicializa el cliente de Google Cloud Vision."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de Google Cloud Vision."""
        try:
            import json
            
            # Prioridad 1: JSON desde variable de entorno (mejor para Render manual)
            if Config.GOOGLE_APPLICATION_CREDENTIALS_JSON:
                credentials_info = json.loads(Config.GOOGLE_APPLICATION_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
            # Prioridad 2: Workload Identity de Render (archivo automático)
            # Intentar usar Application Default Credentials si la variable está configurada
            elif Config.GOOGLE_APPLICATION_CREDENTIALS:
                # Render puede crear el archivo después del inicio, intentar usar ADC
                try:
                    self.client = vision.ImageAnnotatorClient()
                except Exception as e:
                    print(f"Advertencia: No se pudo inicializar con ADC: {e}")
                    # Si el archivo existe, intentar usarlo
                    if os.path.exists(Config.GOOGLE_APPLICATION_CREDENTIALS):
                        self.client = vision.ImageAnnotatorClient()
                    else:
                        print(f"Advertencia: Archivo {Config.GOOGLE_APPLICATION_CREDENTIALS} no existe aún")
                        self.client = None
            # Prioridad 3: Archivo desde ruta personalizada
            elif Config.GOOGLE_CREDENTIALS_PATH and os.path.exists(Config.GOOGLE_CREDENTIALS_PATH):
                credentials = service_account.Credentials.from_service_account_file(
                    Config.GOOGLE_CREDENTIALS_PATH
                )
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                print("Advertencia: No se encontraron credenciales de Google Cloud Vision")
                print("El OCR se inicializará cuando las credenciales estén disponibles")
                self.client = None
        except Exception as e:
            print(f"Error al inicializar cliente de Vision: {e}")
            import traceback
            traceback.print_exc()
            self.client = None
    
    def _ensure_client(self):
        """Asegura que el cliente esté inicializado, reintentando si es necesario."""
        if self.client:
            return
        
        # Reintentar inicialización si no estaba disponible al inicio
        self._initialize_client()
        
        if not self.client:
            raise Exception("Cliente de Google Cloud Vision no inicializado. Verifica las credenciales.")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extrae texto de una imagen usando OCR.
        
        Args:
            image_path: Ruta al archivo de imagen
            
        Returns:
            Texto extraído de la imagen
        """
        self._ensure_client()
        
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        
        if texts:
            return texts[0].description
        return ""
    
    def extract_invoice_data(self, image_path: str) -> Dict:
        """
        Extrae datos estructurados de una factura desde una imagen.
        
        Args:
            image_path: Ruta al archivo de imagen de la factura
            
        Returns:
            Diccionario con datos extraídos de la factura
        """
        self._ensure_client()
        
        # Extraer texto completo
        texto_completo = self.extract_text_from_image(image_path)
        
        # Procesar texto para extraer datos estructurados
        datos = self._parse_invoice_text(texto_completo)
        
        return datos
    
    def _parse_invoice_text(self, texto: str) -> Dict:
        """
        Parsea el texto extraído para obtener datos estructurados de la factura.
        
        Args:
            texto: Texto completo extraído de la factura
            
        Returns:
            Diccionario con datos estructurados
        """
        datos = {
            'numero_factura': None,
            'proveedor': None,
            'ruc': None,
            'fecha': None,
            'items': [],
            'subtotal': None,
            'iva': None,
            'total': None,
        }
        
        lineas = texto.split('\n')
        
        # Buscar número de factura (patrones comunes)
        for linea in lineas:
            linea_lower = linea.lower()
            if 'factura' in linea_lower or 'invoice' in linea_lower:
                # Intentar extraer número
                import re
                numeros = re.findall(r'\d+', linea)
                if numeros:
                    datos['numero_factura'] = '-'.join(numeros[:3]) if len(numeros) >= 3 else numeros[0]
            
            # Buscar RUC
            if 'ruc' in linea_lower:
                ruc_match = re.search(r'\d{10,13}', linea)
                if ruc_match:
                    datos['ruc'] = ruc_match.group()
            
            # Buscar fecha
            fecha_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', linea)
            if fecha_match:
                datos['fecha'] = fecha_match.group()
            
            # Buscar totales
            if 'total' in linea_lower or 'suma' in linea_lower:
                total_match = re.search(r'\d+\.?\d*', linea)
                if total_match:
                    datos['total'] = float(total_match.group())
        
        # Buscar nombre del proveedor (generalmente en las primeras líneas)
        for i, linea in enumerate(lineas[:10]):
            if len(linea.strip()) > 5 and not any(char.isdigit() for char in linea[:5]):
                datos['proveedor'] = linea.strip()
                break
        
        # Buscar items (líneas con cantidades y precios)
        for linea in lineas:
            # Patrón: cantidad descripción precio total
            item_match = re.match(r'(\d+)\s+(.+?)\s+(\d+\.?\d*)\s+(\d+\.?\d*)', linea)
            if item_match:
                cantidad, descripcion, precio, total_item = item_match.groups()
                datos['items'].append({
                    'descripcion': descripcion.strip(),
                    'cantidad': float(cantidad),
                    'precio': float(precio),
                    'total': float(total_item),
                })
        
        return datos

# Instancia global
ocr_processor = OCRProcessor()
