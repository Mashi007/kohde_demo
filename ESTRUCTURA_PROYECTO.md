# Estructura del Proyecto - Kohde Demo ERP

## 📁 Estructura de Directorios

```
kohde_demo/
│
├── 📄 Archivos de Configuración Raíz
│   ├── app.py                    # Aplicación Flask principal
│   ├── config.py                 # Configuración del sistema
│   ├── requirements.txt           # Dependencias Python
│   ├── render.yaml               # Configuración para Render.com
│   ├── .env                      # Variables de entorno (no en git)
│   ├── .env.example              # Ejemplo de variables de entorno
│   ├── .gitignore                # Archivos ignorados por git
│   └── README.md                 # Documentación principal
│
├── 📂 models/                    # Modelos de Base de Datos (SQLAlchemy)
│   ├── __init__.py
│   ├── item.py                   # Modelo de Items/Productos
│   ├── inventario.py             # Modelo de Inventario
│   ├── factura.py                 # Modelo de Facturas
│   ├── receta.py                  # Modelo de Recetas
│   ├── programacion.py            # Modelo de Programación de Menús
│   ├── pedido.py                  # Modelo de Pedidos de Compra
│   ├── pedido_interno.py          # Modelo de Pedidos Internos
│   ├── requerimiento.py           # Modelo de Requerimientos
│   ├── merma.py                   # Modelo de Mermas
│   ├── charola.py                 # Modelo de Charolas
│   ├── costo_item.py              # Modelo de Costos Estandarizados
│   ├── proveedor.py               # Modelo de Proveedores
│   ├── contacto.py                # Modelo de Contactos CRM
│   ├── ticket.py                  # Modelo de Tickets
│   ├── chat.py                    # Modelo de Chats
│   ├── contabilidad.py            # Modelo de Contabilidad
│   └── ... (otros modelos)
│
├── 📂 routes/                     # Rutas API (Endpoints)
│   ├── __init__.py
│   ├── logistica_routes.py        # Rutas de Logística
│   ├── crm_routes.py              # Rutas de CRM
│   ├── contabilidad_routes.py     # Rutas de Contabilidad
│   ├── planificacion_routes.py    # Rutas de Planificación
│   ├── compras_routes.py          # Rutas de Compras
│   ├── configuracion_routes.py     # Rutas de Configuración
│   ├── reportes_routes.py         # Rutas de Reportes
│   ├── chat_routes.py             # Rutas de Chat
│   ├── whatsapp_webhook.py        # Webhook de WhatsApp
│   └── health.py                  # Health check
│
├── 📂 modules/                    # Lógica de Negocio
│   ├── __init__.py
│   │
│   ├── 📂 logistica/              # Módulo de Logística
│   │   ├── __init__.py
│   │   ├── items.py               # Servicio de Items
│   │   ├── inventario.py          # Servicio de Inventario
│   │   ├── facturas.py            # Servicio de Facturas
│   │   ├── pedidos.py             # Servicio de Pedidos
│   │   ├── pedidos_internos.py    # Servicio de Pedidos Internos
│   │   ├── requerimientos.py     # Servicio de Requerimientos
│   │   ├── costos.py              # Servicio de Costos
│   │   ├── compras_stats.py       # Estadísticas de Compras
│   │   ├── pedidos_automaticos.py # Generación Automática
│   │   ├── tareas_programadas.py  # Tareas Programadas
│   │   └── conversor_unidades.py  # Conversión de Unidades
│   │
│   ├── 📂 crm/                    # Módulo de CRM
│   │   ├── __init__.py
│   │   ├── contactos.py           # Servicio de Contactos
│   │   ├── conversaciones.py      # Servicio de Conversaciones
│   │   ├── tickets.py             # Servicio de Tickets
│   │   ├── tickets_automaticos.py # Tickets Automáticos
│   │   └── notificaciones/        # Notificaciones CRM
│   │       ├── email.py
│   │       └── whatsapp.py
│   │
│   ├── 📂 planificacion/          # Módulo de Planificación
│   │   ├── __init__.py
│   │   ├── recetas.py             # Servicio de Recetas
│   │   ├── programacion.py       # Servicio de Programación
│   │   └── requerimientos.py     # Cálculo de Requerimientos
│   │
│   ├── 📂 contabilidad/           # Módulo de Contabilidad
│   │   ├── __init__.py
│   │   └── centro_cuentas.py     # Plan Contable
│   │
│   ├── 📂 configuracion/          # Módulo de Configuración
│   │   ├── __init__.py
│   │   ├── whatsapp.py           # Configuración WhatsApp
│   │   ├── ai.py                 # Configuración AI
│   │   └── notificaciones.py     # Configuración Notificaciones
│   │
│   ├── 📂 chat/                   # Módulo de Chat
│   │   ├── __init__.py
│   │   └── chat_service.py       # Servicio de Chat AI
│   │
│   └── 📂 reportes/               # Módulo de Reportes
│       ├── __init__.py
│       ├── charolas.py
│       └── mermas.py
│
├── 📂 scripts/                    # Scripts de Utilidad
│   ├── init_items.py             # Inicializar Items (50 items)
│   ├── init_facturas.py          # Inicializar Facturas (20 facturas)
│   ├── init_recetas.py           # Inicializar Recetas (12 recetas)
│   ├── init_inventario.py        # Inicializar Inventario
│   ├── init_pedidos.py           # Inicializar Pedidos (10 pedidos)
│   ├── init_pedidos_internos.py  # Inicializar Pedidos Internos (10)
│   ├── init_requerimientos.py    # Inicializar Requerimientos (10)
│   ├── init_mermas.py            # Inicializar Mermas (10)
│   ├── init_charolas.py          # Inicializar Charolas (10)
│   ├── init_costos.py            # Inicializar Costos (10)
│   ├── init_food_labels.py       # Inicializar Labels
│   ├── init_all_data.py          # Script maestro (ejecuta todos)
│   ├── verificar_config.py       # Verificar configuración .env
│   ├── probar_conexion.py        # Probar conexión BD
│   ├── README.md                 # Documentación de scripts
│   ├── EJECUTAR_SCRIPTS.md       # Guía de ejecución
│   └── SOLUCION_ERROR_DB.md       # Solución problemas BD
│
├── 📂 utils/                      # Utilidades
│   ├── __init__.py
│   ├── route_helpers.py          # Helpers para rutas
│   ├── db_helpers.py             # Helpers para BD
│   ├── auth_helpers.py          # Helpers de autenticación
│   ├── validators.py             # Validadores
│   ├── helpers.py                # Helpers generales
│   └── ocr.py                    # OCR (Google Cloud Vision)
│
├── 📂 middleware/                 # Middleware
│   └── cors_handler.py           # Manejo de CORS
│
├── 📂 migrations/                 # Migraciones y Documentación
│   └── (archivos de análisis y migraciones)
│
├── 📂 frontend/                   # Frontend React
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── 📂 uploads/                    # Archivos subidos
│   └── facturas/                 # Facturas subidas
│
└── 📄 Documentación Markdown     # Archivos .md de documentación
    ├── README.md
    ├── MODULO_LOGISTICA_COMPLETO.md
    ├── MODULO_CONTACTOS_CRM.md
    └── ... (más documentación)
```

## 🔑 Archivos Clave

### Configuración
- **`app.py`**: Punto de entrada de la aplicación Flask
- **`config.py`**: Configuración del sistema (BD, APIs, etc.)
- **`.env`**: Variables de entorno (no versionado)
- **`requirements.txt`**: Dependencias Python

### Modelos Principales
- **`models/item.py`**: Items/Productos del inventario
- **`models/inventario.py`**: Control de inventario
- **`models/factura.py`**: Facturas de proveedores
- **`models/receta.py`**: Recetas de cocina
- **`models/programacion.py`**: Programación de menús

### Scripts de Inicialización
- **`scripts/init_items.py`**: Crea 50 items variados
- **`scripts/init_pedidos.py`**: Crea 10 pedidos de compra
- **`scripts/init_pedidos_internos.py`**: Crea 10 pedidos internos
- **`scripts/init_requerimientos.py`**: Crea 10 requerimientos
- **`scripts/init_mermas.py`**: Crea 10 mermas
- **`scripts/init_charolas.py`**: Crea 10 charolas
- **`scripts/init_costos.py`**: Crea 10 costos estandarizados

## 📊 Estadísticas del Proyecto

- **101 archivos Python** (.py)
- **69 archivos Markdown** (.md) de documentación
- **29 tablas** en la base de datos
- **10 módulos principales** de funcionalidad
- **6 scripts de mock data** para logística

## 🚀 Comandos Útiles

```powershell
# Verificar configuración
python scripts/verificar_config.py

# Probar conexión
python scripts/probar_conexion.py

# Inicializar datos base
python scripts/init_items.py
python scripts/init_facturas.py
python scripts/init_recetas.py

# Inicializar módulos de logística
python scripts/init_pedidos.py
python scripts/init_pedidos_internos.py
python scripts/init_requerimientos.py
python scripts/init_mermas.py
python scripts/init_charolas.py
python scripts/init_costos.py
```

## 📝 Notas

- El proyecto usa **PostgreSQL** como base de datos (hosteada en Render.com)
- El frontend está en **React** (carpeta `frontend/`)
- Los scripts son **idempotentes**: pueden ejecutarse múltiples veces sin duplicar datos
- La configuración se carga desde `.env` usando `python-dotenv`
