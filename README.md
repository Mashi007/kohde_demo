# Sistema ERP Multinacional para Cadena de Restaurantes

Sistema ERP modular completo para gestión de restaurantes con integración de WhatsApp Business API, OCR para facturas, control de inventario, planificación de menús y más.

## 🚀 Características Principales

### Módulos Implementados

1. **CRM (Gestión de Relaciones con Clientes)**
   - Base de datos central de clientes
   - Sistema de tickets/quejas
   - Historial de facturas y tickets por cliente

2. **Contabilidad**
   - Ingreso de facturas con OCR (Google Cloud Vision)
   - Plan contable jerárquico
   - Aprobación de facturas y actualización automática de inventario

3. **Logística**
   - Control de inventario en tiempo real
   - Catálogo de items (productos/insumos)
   - Requerimientos (salidas de bodega)
   - Alertas de stock bajo

4. **Compras**
   - Gestión de proveedores
   - Generación automática de pedidos
   - Historial de pedidos y facturas por proveedor

5. **Planificación**
   - Gestión de recetas con cálculo automático de costos y calorías
   - Programación de menús diarios
   - Cálculo automático de necesidades de items
   - Generación automática de pedidos de compra

6. **Notificaciones**
   - Integración con WhatsApp Business API
   - Envío de emails con SendGrid
   - Alertas automáticas de stock bajo
   - Notificaciones de tickets resueltos

## 📋 Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Cuenta de Google Cloud Platform (para OCR)
- Cuenta de WhatsApp Business API (opcional)
- Cuenta de SendGrid (opcional, para emails)

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd erp-restaurantes
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos PostgreSQL

```bash
# Crear base de datos
createdb erp_restaurantes

# Ejecutar schema inicial
psql -U postgres -d erp_restaurantes -f migrations/initial_schema.sql
```

### 5. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y completar las variables:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_restaurantes
DB_USER=postgres
DB_PASSWORD=tu_password

# Flask
SECRET_KEY=tu-secret-key-seguro
DEBUG=True

# Google Cloud Vision (OCR)
GOOGLE_CLOUD_PROJECT=tu-project-id
GOOGLE_CREDENTIALS_PATH=/ruta/a/credentials.json

# WhatsApp Business API (opcional)
WHATSAPP_ACCESS_TOKEN=tu-access-token
WHATSAPP_PHONE_NUMBER_ID=tu-phone-number-id
WHATSAPP_VERIFY_TOKEN=tu-verify-token

# SendGrid (opcional)
SENDGRID_API_KEY=tu-api-key
EMAIL_FROM=noreply@tudominio.com
```

### 6. Configurar Google Cloud Vision API

1. Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar la API de Cloud Vision
3. Crear una cuenta de servicio y descargar el archivo JSON de credenciales
4. Guardar el archivo en una ubicación segura y actualizar `GOOGLE_CREDENTIALS_PATH` en `.env`

### 7. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📚 Estructura del Proyecto

```
erp-restaurantes/
├── app.py                          # Aplicación principal Flask
├── config.py                       # Configuración
├── requirements.txt                # Dependencias Python
├── models/                         # Modelos SQLAlchemy
│   ├── cliente.py
│   ├── proveedor.py
│   ├── factura.py
│   ├── item.py
│   ├── receta.py
│   ├── ticket.py
│   ├── inventario.py
│   ├── pedido.py
│   ├── programacion.py
│   ├── requerimiento.py
│   └── contabilidad.py
├── modules/                        # Módulos de negocio
│   ├── crm/
│   ├── contabilidad/
│   ├── logistica/
│   ├── compras/
│   ├── planificacion/
│   └── notificaciones/
├── routes/                         # Endpoints API
│   ├── crm_routes.py
│   ├── contabilidad_routes.py
│   ├── logistica_routes.py
│   ├── compras_routes.py
│   ├── planificacion_routes.py
│   └── whatsapp_webhook.py
├── utils/                          # Utilidades
│   ├── ocr.py
│   ├── validators.py
│   └── helpers.py
├── migrations/                     # Migraciones DB
│   └── initial_schema.sql
└── uploads/                        # Archivos subidos (facturas)
    └── facturas/
```

## 🔌 API Endpoints

### CRM

- `GET /api/crm/clientes` - Listar clientes
- `POST /api/crm/clientes` - Crear cliente
- `GET /api/crm/clientes/{id}` - Obtener cliente
- `PUT /api/crm/clientes/{id}` - Actualizar cliente
- `GET /api/crm/clientes/{id}/facturas` - Historial de facturas
- `GET /api/crm/tickets` - Listar tickets
- `POST /api/crm/tickets` - Crear ticket
- `POST /api/crm/tickets/{id}/resolver` - Resolver ticket

### Contabilidad

- `GET /api/contabilidad/facturas` - Listar facturas
- `POST /api/contabilidad/facturas/ingresar-imagen` - Ingresar factura con OCR
- `POST /api/contabilidad/facturas/{id}/aprobar` - Aprobar factura
- `GET /api/contabilidad/cuentas` - Listar cuentas contables
- `POST /api/contabilidad/cuentas` - Crear cuenta contable

### Logística

- `GET /api/logistica/items` - Listar items
- `POST /api/logistica/items` - Crear item
- `GET /api/logistica/inventario` - Listar inventario
- `GET /api/logistica/inventario/stock-bajo` - Items con stock bajo
- `POST /api/logistica/requerimientos` - Crear requerimiento
- `POST /api/logistica/requerimientos/{id}/procesar` - Procesar requerimiento

### Compras

- `GET /api/compras/proveedores` - Listar proveedores
- `POST /api/compras/proveedores` - Crear proveedor
- `GET /api/compras/pedidos` - Listar pedidos
- `POST /api/compras/pedidos` - Crear pedido
- `POST /api/compras/pedidos/automatico` - Generar pedido automático
- `POST /api/compras/pedidos/{id}/enviar` - Enviar pedido al proveedor

### Planificación

- `GET /api/planificacion/recetas` - Listar recetas
- `POST /api/planificacion/recetas` - Crear receta
- `GET /api/planificacion/programacion` - Listar programaciones
- `POST /api/planificacion/programacion` - Crear programación
- `GET /api/planificacion/programacion/{id}/necesidades` - Calcular necesidades
- `POST /api/planificacion/programacion/{id}/generar-pedidos` - Generar pedidos automáticos

### WhatsApp Webhook

- `GET /whatsapp/webhook` - Verificación del webhook
- `POST /whatsapp/webhook` - Recibir mensajes de WhatsApp

## 🔄 Flujos Principales

### 1. Ingreso de Factura con OCR

1. Usuario envía imagen de factura por WhatsApp o sube archivo
2. Sistema procesa imagen con Google Cloud Vision OCR
3. Extrae datos: número, proveedor, fecha, items, totales
4. Busca o crea proveedor automáticamente
5. Crea factura en estado "pendiente"
6. Notifica a bodega por WhatsApp

### 2. Aprobación de Factura

1. Bodega ingresa al sistema y revisa factura pendiente
2. Ingresa cantidad recibida por cada item
3. Aprueba factura (total o parcial)
4. Sistema actualiza inventario automáticamente
5. Actualiza costo unitario de items
6. Notifica a contabilidad y proveedor

### 3. Programación de Menú

1. Usuario crea programación para una fecha específica
2. Agrega recetas con cantidad de porciones
3. Sistema calcula necesidades de items automáticamente
4. Compara con inventario actual
5. Genera alertas de items faltantes
6. Genera pedidos automáticos agrupados por proveedor

### 4. Requerimiento de Bodega

1. Usuario selecciona items del catálogo
2. Sistema muestra stock disponible
3. Usuario ingresa cantidad solicitada
4. Sistema valida disponibilidad
5. Crea requerimiento
6. Al procesar, actualiza inventario (salida)

## 🔐 Seguridad

- Variables sensibles en archivo `.env` (no versionar)
- Validación de datos en todos los endpoints
- Sanitización de inputs
- Manejo de errores robusto

## 🧪 Testing

```bash
# Ejecutar tests (cuando se implementen)
pytest
```

## 📦 Despliegue

### Render.com

1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Especificar comando de inicio: `gunicorn app:app`

### AWS / Heroku

Similar proceso, configurando variables de entorno según la plataforma.

## 🐛 Solución de Problemas

### Error de conexión a PostgreSQL

- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos exista

### Error de OCR

- Verificar que Google Cloud Vision API esté habilitada
- Verificar ruta al archivo de credenciales
- Verificar permisos del archivo de credenciales

### Error de WhatsApp

- Verificar tokens en `.env`
- Verificar que el webhook esté configurado correctamente
- Verificar que el servidor sea accesible públicamente (HTTPS requerido)

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte, abre un issue en el repositorio o contacta al equipo de desarrollo.

## 🎯 Roadmap

### Fase 1 (MVP) ✅
- [x] Modelo de datos completo
- [x] Módulo de items (CRUD)
- [x] Ingreso de facturas con OCR básico
- [x] Inventario básico
- [x] WhatsApp webhook para recibir imágenes

### Fase 2 (En desarrollo)
- [ ] Recetas completas con cálculos
- [ ] Programación de menús
- [ ] Generación automática de pedidos
- [ ] Requerimientos de bodega
- [ ] Notificaciones WhatsApp/Email

### Fase 3 (Futuro)
- [ ] CRM completo con tickets
- [ ] Centro de cuentas contable
- [ ] Reportes avanzados
- [ ] Dashboard con KPIs
- [ ] Optimización de procesos
- [ ] Autenticación y autorización de usuarios
- [ ] Sistema de roles y permisos

---

**Desarrollado con ❤️ para la gestión eficiente de restaurantes**
