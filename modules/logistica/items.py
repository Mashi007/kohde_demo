"""
Lógica de negocio para gestión de items (catálogo de productos).
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from datetime import datetime
from models import Item, Inventario, ItemLabel, FacturaItem, Factura
from models.factura import EstadoFactura
from utils.validators import validate_positive_number

class ItemService:
    """Servicio para gestión de items."""
    
    @staticmethod
    def generar_codigo_automatico(db: Session, categoria: str, nombre: str = None) -> str:
        """
        Genera un código automático para un item.
        
        Formato: CAT-YYYYMMDD-NNNN
        Donde:
        - CAT: Prefijo según categoría (MP, IN, PT, BE, LI, OT)
        - YYYYMMDD: Fecha actual
        - NNNN: Número secuencial del día
        
        Args:
            db: Sesión de base de datos
            categoria: Categoría del item
            nombre: Nombre del item (opcional, para generar código alternativo)
            
        Returns:
            Código generado
        """
        # Prefijos por categoría
        prefijos = {
            'materia_prima': 'MP',
            'insumo': 'IN',
            'producto_terminado': 'PT',
            'bebida': 'BE',
            'limpieza': 'LI',
            'otros': 'OT'
        }
        
        prefijo = prefijos.get(categoria.lower(), 'IT')
        fecha = datetime.now().strftime('%Y%m%d')
        
        # Buscar el último código del día con este prefijo
        patron_codigo = f"{prefijo}-{fecha}-%"
        ultimo_item = db.query(Item).filter(
            Item.codigo.like(patron_codigo)
        ).order_by(Item.codigo.desc()).first()
        
        # Obtener el siguiente número secuencial
        if ultimo_item:
            try:
                # Extraer el número del último código
                partes = ultimo_item.codigo.split('-')
                if len(partes) == 3:
                    ultimo_numero = int(partes[2])
                    siguiente_numero = ultimo_numero + 1
                else:
                    siguiente_numero = 1
            except (ValueError, IndexError):
                siguiente_numero = 1
        else:
            siguiente_numero = 1
        
        # Generar código con formato: CAT-YYYYMMDD-NNNN
        codigo = f"{prefijo}-{fecha}-{siguiente_numero:04d}"
        
        # Verificar que no exista (por si acaso)
        while db.query(Item).filter(Item.codigo == codigo).first():
            siguiente_numero += 1
            codigo = f"{prefijo}-{fecha}-{siguiente_numero:04d}"
        
        return codigo
    
    @staticmethod
    def crear_item(db: Session, datos: Dict) -> Item:
        """
        Crea un nuevo item.
        
        Args:
            db: Sesión de base de datos
            datos: Diccionario con datos del item
            
        Returns:
            Item creado
        """
        # Generar código automático si no se proporciona o está vacío
        codigo_proporcionado = datos.get('codigo', '').strip() if datos.get('codigo') else ''
        if not codigo_proporcionado:
            categoria = datos.get('categoria', 'otros')
            # Convertir string a enum si es necesario
            if isinstance(categoria, str):
                from models.item import CategoriaItem
                try:
                    categoria_enum = CategoriaItem[categoria.upper()]
                    categoria_str = categoria_enum.value
                except KeyError:
                    categoria_str = categoria.lower()
            else:
                categoria_str = categoria.value if hasattr(categoria, 'value') else str(categoria)
            
            nombre = datos.get('nombre', '')
            datos['codigo'] = ItemService.generar_codigo_automatico(db, categoria_str, nombre)
        
        # Validar código único
        if datos.get('codigo'):
            existente = db.query(Item).filter(Item.codigo == datos['codigo']).first()
            if existente:
                raise ValueError("Ya existe un item con este código")
        
        # Separar labels del resto de datos
        label_ids = datos.pop('label_ids', [])
        
        item = Item(**datos)
        db.add(item)
        db.commit()
        db.refresh(item)
        
        # Asignar labels si se proporcionaron
        if label_ids:
            labels = db.query(ItemLabel).filter(ItemLabel.id.in_(label_ids)).all()
            item.labels = labels
            db.commit()
            db.refresh(item)
        
        # Crear registro de inventario inicial si se especifica cantidad inicial
        if 'cantidad_inicial' in datos:
            inventario = Inventario(
                item_id=item.id,
                cantidad_actual=float(datos['cantidad_inicial']),
                unidad=item.unidad,
                cantidad_minima=float(datos.get('cantidad_minima', 0))
            )
            db.add(inventario)
            db.commit()
        
        return item
    
    @staticmethod
    def obtener_item(db: Session, item_id: int) -> Optional[Item]:
        """Obtiene un item por ID."""
        return db.query(Item).filter(Item.id == item_id).first()
    
    @staticmethod
    def listar_items(
        db: Session,
        categoria: Optional[str] = None,
        activo: Optional[bool] = None,
        busqueda: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Item]:
        """
        Lista items con filtros opcionales.
        
        Args:
            db: Sesión de base de datos
            categoria: Filtrar por categoría
            activo: Filtrar por estado activo
            busqueda: Búsqueda por nombre o código
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de items
        """
        query = db.query(Item)
        
        if categoria:
            from models.item import CategoriaItem
            query = query.filter(Item.categoria == CategoriaItem[categoria.upper()])
        
        if activo is not None:
            query = query.filter(Item.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Item.nombre.ilike(f'%{busqueda}%'),
                    Item.codigo.ilike(f'%{busqueda}%')
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_item(db: Session, item_id: int, datos: Dict) -> Item:
        """
        Actualiza un item existente.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            datos: Datos a actualizar
            
        Returns:
            Item actualizado
        """
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        # Validar código único si se cambia
        if 'codigo' in datos and datos['codigo'] != item.codigo:
            existente = db.query(Item).filter(Item.codigo == datos['codigo']).first()
            if existente:
                raise ValueError("Ya existe un item con este código")
        
        # Separar labels del resto de datos
        label_ids = datos.pop('label_ids', None)
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(item, key) and key != 'id':
                if key in ['categoria']:
                    from models.item import CategoriaItem
                    if isinstance(value, str):
                        value = CategoriaItem[value.upper()]
                setattr(item, key, value)
        
        # Actualizar labels si se proporcionaron
        if label_ids is not None:
            labels = db.query(ItemLabel).filter(ItemLabel.id.in_(label_ids)).all()
            item.labels = labels
        
        db.commit()
        db.refresh(item)
        return item
    
    @staticmethod
    def calcular_costo_unitario_promedio(db: Session, item_id: int) -> Optional[float]:
        """
        Calcula el costo unitario promedio basado en las últimas 3 facturas aprobadas.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            
        Returns:
            Costo unitario promedio o None si no hay facturas aprobadas
        """
        # Obtener las últimas 3 facturas aprobadas que contengan este item
        facturas_items = db.query(FacturaItem).join(Factura).filter(
            FacturaItem.item_id == item_id,
            Factura.estado == EstadoFactura.APROBADA,
            FacturaItem.cantidad_aprobada.isnot(None),
            FacturaItem.cantidad_aprobada > 0,
            FacturaItem.precio_unitario.isnot(None),
            FacturaItem.precio_unitario > 0
        ).order_by(desc(Factura.fecha_aprobacion)).limit(3).all()
        
        if not facturas_items:
            return None
        
        # Calcular el promedio de los precios unitarios
        precios = [float(fi.precio_unitario) for fi in facturas_items if fi.precio_unitario]
        if not precios:
            return None
        
        promedio = sum(precios) / len(precios)
        return round(promedio, 2)
    
    @staticmethod
    def obtener_item_con_costo(db: Session, item_id: int) -> Optional[Dict]:
        """
        Obtiene un item con su costo unitario calculado.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            
        Returns:
            Diccionario con el item y su costo unitario calculado
        """
        item = ItemService.obtener_item(db, item_id)
        if not item:
            return None
        
        item_dict = item.to_dict()
        costo_promedio = ItemService.calcular_costo_unitario_promedio(db, item_id)
        item_dict['costo_unitario_promedio'] = costo_promedio
        
        return item_dict
    
    @staticmethod
    def actualizar_costo_unitario(db: Session, item_id: int, costo: float) -> Item:
        """
        Actualiza el costo unitario de un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            costo: Nuevo costo unitario
            
        Returns:
            Item actualizado
        """
        if not validate_positive_number(costo):
            raise ValueError("El costo debe ser un número positivo")
        
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        item.costo_unitario_actual = costo
        
        # Actualizar también en inventario si existe
        inventario = db.query(Inventario).filter(Inventario.item_id == item_id).first()
        if inventario:
            inventario.ultimo_costo_unitario = costo
        
        db.commit()
        db.refresh(item)
        return item
