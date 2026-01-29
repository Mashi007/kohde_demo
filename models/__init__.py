"""
Modelos de base de datos del ERP.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar todos los modelos para que SQLAlchemy los registre
# Cliente removido (módulo eliminado)
from models.proveedor import Proveedor
from models.factura import Factura, FacturaItem
from models.item import Item
from models.receta import Receta, RecetaIngrediente
from models.ticket import Ticket
from models.inventario import Inventario
from models.pedido import PedidoCompra, PedidoCompraItem
from models.programacion import ProgramacionMenu, ProgramacionMenuItem
from models.requerimiento import Requerimiento, RequerimientoItem
from models.contabilidad import CuentaContable
from models.charola import Charola, CharolaItem
from models.merma import Merma
from models.chat import Conversacion, Mensaje

__all__ = [
    'db',
    # 'Cliente',  # Removido
    'Proveedor',
    'Factura',
    'FacturaItem',
    'Item',
    'Receta',
    'RecetaIngrediente',
    'Ticket',
    'Inventario',
    'PedidoCompra',
    'PedidoCompraItem',
    'ProgramacionMenu',
    'ProgramacionMenuItem',
    'Requerimiento',
    'RequerimientoItem',
    'CuentaContable',
    'Charola',
    'CharolaItem',
    'Merma',
    'Conversacion',
    'Mensaje',
]
