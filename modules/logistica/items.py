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
        
        # Convertir categoria string a valor que PostgreSQL espera
        # PostgreSQL tiene valores mixtos: algunos en MAYÚSCULAS (nombres) y otros en minúsculas (valores)
        if 'categoria' in datos and isinstance(datos['categoria'], str):
            from models.item import CategoriaItem
            categoria_str = datos['categoria'].upper().strip()
            categoria_lower = datos['categoria'].lower().strip()
            
            # Mapeo de valores Python a valores PostgreSQL
            categoria_pg_map = {
                'MATERIA_PRIMA': 'MATERIA_PRIMA',  # Nombre en mayúsculas
                'INSUMO': 'INSUMO',  # Nombre en mayúsculas
                'PRODUCTO_TERMINADO': 'PRODUCTO_TERMINADO',  # Nombre en mayúsculas
                'BEBIDA': 'bebida',  # Valor en minúsculas
                'LIMPIEZA': 'limpieza',  # Valor en minúsculas
                'OTROS': 'otros',  # Valor en minúsculas
                # También aceptar valores en minúsculas y convertirlos
                'materia_prima': 'MATERIA_PRIMA',
                'insumo': 'INSUMO',
                'producto_terminado': 'PRODUCTO_TERMINADO',
                'bebida': 'bebida',
                'limpieza': 'limpieza',
                'otros': 'otros',
            }
            
            # Buscar el valor en el mapa
            if categoria_str in categoria_pg_map:
                datos['categoria'] = categoria_pg_map[categoria_str]
            elif categoria_lower in categoria_pg_map:
                datos['categoria'] = categoria_pg_map[categoria_lower]
            else:
                # Intentar buscar por nombre del enum
                try:
                    cat_enum = CategoriaItem[categoria_str]
                    # Convertir a valor PostgreSQL según el mapeo
                    if cat_enum in [CategoriaItem.MATERIA_PRIMA, CategoriaItem.INSUMO, CategoriaItem.PRODUCTO_TERMINADO]:
                        datos['categoria'] = cat_enum.name  # Usar nombre (mayúsculas)
                    else:
                        datos['categoria'] = cat_enum.value  # Usar valor (minúsculas)
                except KeyError:
                    # Si no se encuentra, usar OTROS por defecto
                    datos['categoria'] = 'otros'
        
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
        from sqlalchemy.orm import selectinload
        
        # Verificar que la sesión esté activa
        if not db.is_active:
            import logging
            logging.warning("Sesión de base de datos inactiva en listar_items")
            try:
                db.rollback()
            except:
                pass
        
        query = db.query(Item)
        
        # Usar eager loading para labels para evitar problemas de lazy loading
        # Verificar primero si la tabla existe antes de intentar eager loading
        try:
            from sqlalchemy import inspect as sql_inspect
            inspector = sql_inspect(db.bind)
            tables = inspector.get_table_names()
            
            # Solo usar eager loading si las tablas necesarias existen
            if 'item_labels' in tables and 'item_label' in tables:
                try:
                    query = query.options(selectinload(Item.labels))
                except Exception as e:
                    import logging
                    logging.warning(f"Error configurando eager loading: {str(e)}")
                    # Continuar sin eager loading si falla
            else:
                import logging
                logging.debug("Tablas item_labels o item_label no existen, omitiendo eager loading")
        except Exception as e:
            import logging
            logging.warning(f"Error verificando tablas para eager loading: {str(e)}")
            # Continuar sin eager loading si falla la verificación
        
        if categoria:
            # Convertir categoria a formato PostgreSQL (valores mixtos)
            categoria_str = categoria.lower().strip()
            categoria_upper = categoria.upper().strip()
            
            # Mapeo de valores Python a valores PostgreSQL
            categoria_pg_map = {
                'materia_prima': 'MATERIA_PRIMA',
                'insumo': 'INSUMO',
                'producto_terminado': 'PRODUCTO_TERMINADO',
                'bebida': 'bebida',
                'limpieza': 'limpieza',
                'otros': 'otros',
                'MATERIA_PRIMA': 'MATERIA_PRIMA',
                'INSUMO': 'INSUMO',
                'PRODUCTO_TERMINADO': 'PRODUCTO_TERMINADO',
                'BEBIDA': 'bebida',
                'LIMPIEZA': 'limpieza',
                'OTROS': 'otros',
            }
            
            # Obtener el valor PostgreSQL esperado
            categoria_pg_value = categoria_pg_map.get(categoria_str) or categoria_pg_map.get(categoria_upper)
            
            if categoria_pg_value:
                # Comparar directamente con el string (PG_ENUM devuelve strings)
                query = query.filter(Item.categoria == categoria_pg_value)
            else:
                # Si no se encuentra en el mapa, intentar comparar directamente
                query = query.filter(Item.categoria == categoria_str)
        
        if activo is not None:
            query = query.filter(Item.activo == activo)
        
        if busqueda:
            query = query.filter(
                or_(
                    Item.nombre.ilike(f'%{busqueda}%'),
                    Item.codigo.ilike(f'%{busqueda}%')
                )
            )
        
        # Ejecutar query con manejo de errores
        try:
            items = query.offset(skip).limit(limit).all()
            return items
        except LookupError as enum_error:
            # Error específico de enum - puede ser que el enum de PostgreSQL tenga valores diferentes
            import logging
            import traceback
            logging.error(f"Error de enum al ejecutar query de items: {str(enum_error)}")
            logging.error(traceback.format_exc())
            # Intentar rollback y retornar lista vacía
            try:
                db.rollback()
            except:
                pass
            # Retornar lista vacía en lugar de fallar
            logging.warning("Retornando lista vacía debido a error de enum. Verificar valores de categoría en la BD.")
            return []
        except Exception as e:
            import logging
            import traceback
            logging.error(f"Error ejecutando query de items: {str(e)}")
            logging.error(traceback.format_exc())
            # Intentar rollback y retornar lista vacía
            try:
                db.rollback()
            except:
                pass
            # Retornar lista vacía en lugar de fallar
            return []
    
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
        
        # Convertir categoria string a valor que PostgreSQL espera (igual que en crear_item)
        if 'categoria' in datos and isinstance(datos['categoria'], str):
            from models.item import CategoriaItem
            categoria_str = datos['categoria'].upper().strip()
            categoria_lower = datos['categoria'].lower().strip()
            
            # Mapeo de valores Python a valores PostgreSQL
            categoria_pg_map = {
                'MATERIA_PRIMA': 'MATERIA_PRIMA',
                'INSUMO': 'INSUMO',
                'PRODUCTO_TERMINADO': 'PRODUCTO_TERMINADO',
                'BEBIDA': 'bebida',
                'LIMPIEZA': 'limpieza',
                'OTROS': 'otros',
                'materia_prima': 'MATERIA_PRIMA',
                'insumo': 'INSUMO',
                'producto_terminado': 'PRODUCTO_TERMINADO',
                'bebida': 'bebida',
                'limpieza': 'limpieza',
                'otros': 'otros',
            }
            
            if categoria_str in categoria_pg_map:
                datos['categoria'] = categoria_pg_map[categoria_str]
            elif categoria_lower in categoria_pg_map:
                datos['categoria'] = categoria_pg_map[categoria_lower]
            else:
                try:
                    cat_enum = CategoriaItem[categoria_str]
                    if cat_enum in [CategoriaItem.MATERIA_PRIMA, CategoriaItem.INSUMO, CategoriaItem.PRODUCTO_TERMINADO]:
                        datos['categoria'] = cat_enum.name
                    else:
                        datos['categoria'] = cat_enum.value
                except KeyError:
                    datos['categoria'] = 'otros'
        
        # Actualizar campos
        for key, value in datos.items():
            if hasattr(item, key) and key != 'id':
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
        try:
            # Verificar que la sesión esté activa
            if not db.is_active:
                import logging
                logging.warning(f"Sesión de base de datos inactiva para item {item_id}")
                return None
            
            # Verificar que las tablas necesarias existan antes de hacer la query
            # Si las tablas no existen o están vacías, retornar None sin error
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.bind)
                tables = inspector.get_table_names()
                
                if 'factura_items' not in tables or 'facturas' not in tables:
                    import logging
                    logging.debug(f"Tablas de facturas no existen para calcular costo promedio del item {item_id}")
                    return None
            except Exception as table_check_error:
                # Si no se puede verificar, continuar (puede ser que inspect no funcione en algunos casos)
                import logging
                logging.debug(f"No se pudo verificar existencia de tablas: {str(table_check_error)}")
            
            # Obtener las últimas 3 facturas aprobadas que contengan este item
            # Usar with_entities para seleccionar solo las columnas necesarias y evitar problemas con columnas faltantes
            try:
                facturas_items = db.query(
                    FacturaItem.precio_unitario,
                    FacturaItem.cantidad_aprobada
                ).join(Factura).filter(
                    FacturaItem.item_id == item_id,
                    Factura.estado == EstadoFactura.APROBADA,
                    FacturaItem.cantidad_aprobada.isnot(None),
                    FacturaItem.cantidad_aprobada > 0,
                    FacturaItem.precio_unitario.isnot(None),
                    FacturaItem.precio_unitario > 0
                ).order_by(desc(Factura.fecha_aprobacion)).limit(3).all()
            except Exception as query_error:
                # Si hay error en la query (tablas no existen, columnas faltantes, etc.)
                import logging
                import traceback
                logging.warning(f"Error en query de facturas para item {item_id}: {str(query_error)}")
                logging.debug(traceback.format_exc())
                try:
                    if db.is_active:
                        db.rollback()
                except:
                    pass
                return None
            
            if not facturas_items:
                return None
            
            # Calcular el promedio de los precios unitarios
            precios = [float(fi.precio_unitario) for fi in facturas_items if fi.precio_unitario]
            if not precios:
                return None
            
            promedio = sum(precios) / len(precios)
            return round(promedio, 2)
        except Exception as e:
            # Si hay un error, hacer rollback y retornar None
            import logging
            import traceback
            try:
                if db.is_active:
                    db.rollback()
            except:
                pass
            logging.warning(f"Error calculando costo promedio para item {item_id}: {str(e)}")
            logging.debug(traceback.format_exc())
            return None
    
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
    def eliminar_item(db: Session, item_id: int) -> bool:
        """
        Elimina un item (soft delete marcándolo como inactivo).
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            
        Returns:
            True si se eliminó correctamente
        """
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        # Soft delete: marcar como inactivo en lugar de eliminar físicamente
        item.activo = False
        db.commit()
        return True
    
    @staticmethod
    def toggle_activo(db: Session, item_id: int) -> Item:
        """
        Activa o desactiva un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            
        Returns:
            Item actualizado
        """
        item = ItemService.obtener_item(db, item_id)
        if not item:
            raise ValueError("Item no encontrado")
        
        item.activo = not item.activo
        db.commit()
        db.refresh(item)
        return item
    
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
