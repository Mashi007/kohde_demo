"""
Servicio para gestionar y proporcionar datos mock.
Permite que el AI acceda a datos de demostración cuando la BD está vacía.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random

class MockDataService:
    """Servicio para gestionar datos mock."""
    
    @staticmethod
    def obtener_mock_charolas(fecha: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """
        Retorna charolas mock para una fecha específica o fecha actual.
        IMPORTANTE: 1 charola = 1 persona servida (coherente para demo).
        Para fecha específica (29 de enero), retorna 196 charolas (196 personas).
        Para otras fechas, retorna número aleatorio coherente (150-200).
        """
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                # Para fecha específica (29 de enero), usar número fijo coherente
                if '29' in fecha or fecha == '2026-01-29':
                    num_personas = 196  # Número fijo para consistencia en demo
                else:
                    num_personas = random.randint(150, 200)
            except:
                fecha_obj = datetime.now()
                num_personas = random.randint(150, 200)
        else:
            fecha_obj = datetime.now()
            num_personas = random.randint(150, 200)
        
        # Generar charolas: 1 charola = 1 persona (coherente)
        charolas = []
        for i in range(1, min(num_personas + 1, limit + 1)):  # Limitar para no generar demasiadas
            # Distribuir entre ubicaciones y tipos de comida de forma realista
            ubicacion = 'Restaurante_A' if i % 2 == 0 else 'Restaurante_B'
            tipo_comida = 'desayuno' if i % 3 == 0 else ('almuerzo' if i % 3 == 1 else 'cena')
            
            charolas.append({
                'id': i,
                'numero_charola': f'CHR-{fecha_obj.strftime("%Y%m%d")}-{i:03d}',
                'fecha_servicio': fecha_obj.isoformat(),
                'ubicacion': ubicacion,
                'tipo_comida': tipo_comida,
                'total_porciones': 1,  # 1 persona por charola (coherente)
                'observaciones': None
            })
        
        return charolas
    
    @staticmethod
    def obtener_mock_facturas() -> List[Dict]:
        """Retorna facturas mock."""
        return [
            {
                'id': 1,
                'numero_factura': 'FAC-2026-001',
                'tipo': 'compra',
                'proveedor_id': 1,
                'fecha_emision': (datetime.now() - timedelta(days=5)).isoformat(),
                'fecha_recepcion': (datetime.now() - timedelta(days=3)).isoformat(),
                'subtotal': 1500.00,
                'iva': 240.00,
                'total': 1740.00,
                'estado': 'pendiente'
            },
            {
                'id': 2,
                'numero_factura': 'FAC-2026-002',
                'tipo': 'compra',
                'proveedor_id': 2,
                'fecha_emision': (datetime.now() - timedelta(days=10)).isoformat(),
                'fecha_recepcion': (datetime.now() - timedelta(days=8)).isoformat(),
                'subtotal': 2300.00,
                'iva': 368.00,
                'total': 2668.00,
                'estado': 'aprobada'
            }
        ]
    
    @staticmethod
    def obtener_mock_items() -> List[Dict]:
        """Retorna items mock."""
        return [
            {
                'id': 1,
                'codigo': 'ITEM-001',
                'nombre': 'Pollo',
                'categoria': 'materia_prima',
                'unidad': 'kg',
                'activo': True,
                'costo_unitario_actual': 8.50
            },
            {
                'id': 2,
                'codigo': 'ITEM-002',
                'nombre': 'Arroz',
                'categoria': 'materia_prima',
                'unidad': 'kg',
                'activo': True,
                'costo_unitario_actual': 1.20
            },
            {
                'id': 3,
                'codigo': 'ITEM-003',
                'nombre': 'Yogurt',
                'categoria': 'bebida',
                'unidad': 'unidad',
                'activo': True,
                'costo_unitario_actual': 2.50
            }
        ]
    
    @staticmethod
    def obtener_mock_inventario() -> List[Dict]:
        """Retorna inventario mock."""
        return [
            {
                'id': 1,
                'item_id': 1,
                'ubicacion': 'bodega_principal',
                'cantidad_actual': 150.50,
                'cantidad_minima': 50.00,
                'unidad': 'kg'
            },
            {
                'id': 2,
                'item_id': 2,
                'ubicacion': 'bodega_principal',
                'cantidad_actual': 200.00,
                'cantidad_minima': 100.00,
                'unidad': 'kg'
            },
            {
                'id': 3,
                'item_id': 3,
                'ubicacion': 'nevera_principal',
                'cantidad_actual': 45,
                'cantidad_minima': 20,
                'unidad': 'unidad'
            }
        ]
    
    @staticmethod
    def obtener_mock_proveedores() -> List[Dict]:
        """Retorna proveedores mock."""
        return [
            {
                'id': 1,
                'nombre': 'Distribuidora Central',
                'ruc': '1234567890001',
                'telefono': '0987654321',
                'email': 'contacto@distribuidora.com',
                'activo': True
            },
            {
                'id': 2,
                'nombre': 'Carnes Premium',
                'ruc': '9876543210001',
                'telefono': '0912345678',
                'email': 'ventas@carnespremium.com',
                'activo': True
            }
        ]
    
    @staticmethod
    def consultar_mock_data(query: str, db: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Simula una consulta SQL sobre datos mock.
        Analiza la consulta SQL y retorna datos mock correspondientes.
        
        Args:
            query: Consulta SQL (se analiza para determinar qué datos retornar)
            db: Sesión de BD (no se usa, solo para compatibilidad)
            
        Returns:
            Diccionario con resultados mock o None si no hay match
        """
        query_upper = query.upper()
        query_lower = query.lower()
        
        # Detectar tipo de consulta basado en palabras clave y estructura SQL
        # CHAROLAS
        if 'CHAROLAS' in query_upper or 'CHAROLA' in query_upper:
            if 'COUNT' in query_upper or 'SUM' in query_upper:
                # Consulta agregada
                # IMPORTANTE: total_porciones = número de personas servidas
                # Si preguntan por personas, retornar SUM(total_porciones)
                # Si preguntan por charolas, retornar COUNT(*)
                
                # Para consultas agregadas, generar números coherentes
                # REGLA: 1 charola = 1 persona servida (coherente para demo)
                # Si preguntan por personas servidas, generar número realista (150-200)
                # Si preguntan por charolas, debe ser igual al número de personas
                
                if '29' in query or '2026-01-29' in query:
                    # Fecha específica (29 de enero): usar número fijo coherente
                    total_personas = 196
                    total_charolas = 196  # 1 charola = 1 persona ✅ COHERENTE
                else:
                    import random
                    total_personas = random.randint(150, 200)
                    total_charolas = total_personas  # 1 charola = 1 persona (coherente)
                
                # Detectar qué está preguntando la consulta
                if 'PERSONAS' in query_upper or 'PERSONA' in query_upper or 'SUM' in query_upper:
                    # Pregunta sobre personas servidas
                    return {
                        'error': None,
                        'resultados': [
                            {
                                'total_personas': total_personas,
                                'total_charolas': total_charolas,
                                'personas_servidas': total_personas
                            }
                        ],
                        'total_filas': 1,
                        'is_mock': True
                    }
                else:
                    # Pregunta sobre número de charolas
                    return {
                        'error': None,
                        'resultados': [
                            {
                                'total_charolas': total_charolas,
                                'total_personas': total_personas
                            }
                        ],
                        'total_filas': 1,
                        'is_mock': True
                    }
            else:
                # Consulta de lista - retornar muestra representativa de charolas
                if '29' in query or '2026-01-29' in query:
                    # Para fecha específica, retornar muestra (primeras 20) pero indicar total real
                    charolas = MockDataService.obtener_mock_charolas('2026-01-29', limit=20)
                    return {
                        'error': None,
                        'resultados': charolas,
                        'total_filas': len(charolas),
                        'is_mock': True,
                        'total_real': 196,  # Total real: 196 charolas = 196 personas
                        'nota': 'Mostrando muestra de 20 charolas. Total: 196 charolas (196 personas)'
                    }
                else:
                    charolas = MockDataService.obtener_mock_charolas(limit=20)
                    total_real = random.randint(150, 200)
                    return {
                        'error': None,
                        'resultados': charolas,
                        'total_filas': len(charolas),
                        'is_mock': True,
                        'total_real': total_real,
                        'nota': f'Mostrando muestra de 20 charolas. Total: {total_real} charolas ({total_real} personas)'
                    }
        
        elif 'FACTURAS' in query_upper or 'FACTURA' in query_upper:
            if 'COUNT' in query_upper:
                return {
                    'error': None,
                    'resultados': [{'count': len(MockDataService.obtener_mock_facturas())}],
                    'total_filas': 1,
                    'is_mock': True
                }
            else:
                return {
                    'error': None,
                    'resultados': MockDataService.obtener_mock_facturas(),
                    'total_filas': 2,
                    'is_mock': True
                }
        
        elif 'ITEMS' in query_upper or 'ITEM' in query_upper:
            if 'INVENTARIO' in query_upper:
                return {
                    'error': None,
                    'resultados': MockDataService.obtener_mock_inventario(),
                    'total_filas': 3,
                    'is_mock': True
                }
            else:
                return {
                    'error': None,
                    'resultados': MockDataService.obtener_mock_items(),
                    'total_filas': 3,
                    'is_mock': True
                }
        
        elif 'PROVEEDORES' in query_upper or 'PROVEEDOR' in query_upper:
            return {
                'error': None,
                'resultados': MockDataService.obtener_mock_proveedores(),
                'total_filas': 2,
                'is_mock': True
            }
        
        elif 'INVENTARIO' in query_upper:
            return {
                'error': None,
                'resultados': MockDataService.obtener_mock_inventario(),
                'total_filas': 3,
                'is_mock': True
            }
        
        # PEDIDOS DE COMPRA
        elif 'PEDIDOS_COMPRA' in query_upper or ('PEDIDO' in query_upper and 'COMPRA' in query_upper):
            if 'COUNT' in query_upper or 'SUM' in query_upper:
                return {
                    'error': None,
                    'resultados': [{'count': 2, 'total': 3500.00}],
                    'total_filas': 1,
                    'is_mock': True
                }
            else:
                return {
                    'error': None,
                    'resultados': [
                        {
                            'id': 1,
                            'proveedor_id': 1,
                            'fecha_pedido': (datetime.now() - timedelta(days=5)).isoformat(),
                            'estado': 'enviado',
                            'total': 1500.00
                        },
                        {
                            'id': 2,
                            'proveedor_id': 2,
                            'fecha_pedido': (datetime.now() - timedelta(days=2)).isoformat(),
                            'estado': 'borrador',
                            'total': 2000.00
                        }
                    ],
                    'total_filas': 2,
                    'is_mock': True
                }
        
        # RECETAS
        elif 'RECETAS' in query_upper or 'RECETA' in query_upper:
            return {
                'error': None,
                'resultados': [
                    {
                        'id': 1,
                        'nombre': 'Arroz con Pollo',
                        'tipo': 'almuerzo',
                        'porciones': 10,
                        'activa': True,
                        'costo_por_porcion': 2.50
                    },
                    {
                        'id': 2,
                        'nombre': 'Huevos Revueltos',
                        'tipo': 'desayuno',
                        'porciones': 8,
                        'activa': True,
                        'costo_por_porcion': 1.80
                    }
                ],
                'total_filas': 2,
                'is_mock': True
            }
        
        # MERMAS
        elif 'MERMAS' in query_upper or 'MERMA' in query_upper:
            return {
                'error': None,
                'resultados': [
                    {
                        'id': 1,
                        'item_id': 1,
                        'cantidad': 5.5,
                        'tipo': 'perdida',
                        'fecha_merma': (datetime.now() - timedelta(days=2)).isoformat(),
                        'motivo': 'Vencimiento'
                    },
                    {
                        'id': 2,
                        'item_id': 3,
                        'cantidad': 2,
                        'tipo': 'danio',
                        'fecha_merma': (datetime.now() - timedelta(days=1)).isoformat(),
                        'motivo': 'Manejo incorrecto'
                    }
                ],
                'total_filas': 2,
                'is_mock': True
            }
        
        # PROGRAMACION MENU
        elif 'PROGRAMACION_MENU' in query_upper or ('PROGRAMACION' in query_upper and 'MENU' in query_upper):
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            return {
                'error': None,
                'resultados': [
                    {
                        'id': 1,
                        'fecha': fecha_hoy,
                        'ubicacion': 'Restaurante_A',
                        'tiempo_comida': 'desayuno',
                        'activa': True
                    },
                    {
                        'id': 2,
                        'fecha': fecha_hoy,
                        'ubicacion': 'Restaurante_A',
                        'tiempo_comida': 'almuerzo',
                        'activa': True
                    }
                ],
                'total_filas': 2,
                'is_mock': True
            }
        
        # REQUERIMIENTOS
        elif 'REQUERIMIENTOS' in query_upper or 'REQUERIMIENTO' in query_upper:
            return {
                'error': None,
                'resultados': [
                    {
                        'id': 1,
                        'fecha': datetime.now().isoformat(),
                        'estado': 'pendiente',
                        'ubicacion': 'Restaurante_A'
                    }
                ],
                'total_filas': 1,
                'is_mock': True
            }
        
        # TICKETS
        elif 'TICKETS' in query_upper or 'TICKET' in query_upper:
            return {
                'error': None,
                'resultados': [
                    {
                        'id': 1,
                        'asunto': 'Problema con factura',
                        'estado': 'abierto',
                        'prioridad': 'media',
                        'fecha_creacion': (datetime.now() - timedelta(days=1)).isoformat()
                    }
                ],
                'total_filas': 1,
                'is_mock': True
            }
        
        # CONSULTAS DE CONTEO GENERAL
        elif 'COUNT(*)' in query_upper and 'FROM' in query_upper:
            # Intentar detectar tabla
            tabla = None
            for tabla_nombre in ['CHAROLAS', 'FACTURAS', 'ITEMS', 'PROVEEDORES', 'INVENTARIO']:
                if tabla_nombre in query_upper:
                    tabla = tabla_nombre.lower()
                    break
            
            if tabla == 'charolas':
                return {
                    'error': None,
                    'resultados': [{'count': 3}],
                    'total_filas': 1,
                    'is_mock': True
                }
            elif tabla == 'facturas':
                return {
                    'error': None,
                    'resultados': [{'count': 2}],
                    'total_filas': 1,
                    'is_mock': True
                }
            elif tabla == 'items':
                return {
                    'error': None,
                    'resultados': [{'count': 3}],
                    'total_filas': 1,
                    'is_mock': True
                }
            elif tabla == 'proveedores':
                return {
                    'error': None,
                    'resultados': [{'count': 2}],
                    'total_filas': 1,
                    'is_mock': True
                }
            elif tabla == 'inventario':
                return {
                    'error': None,
                    'resultados': [{'count': 3}],
                    'total_filas': 1,
                    'is_mock': True
                }
        
        # Si no hay match, retornar None para que se use BD real
        return None
