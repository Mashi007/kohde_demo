# 📇 MÓDULO DE CONTACTOS - CRM

## ✅ IMPLEMENTACIÓN COMPLETA

Se ha desarrollado el módulo de Contactos en CRM con capacidad de conversación por Email y WhatsApp.

---

## 🗄️ BASE DE DATOS

### Tabla: `contactos`

**Campos:**
- `id` (SERIAL PRIMARY KEY)
- `nombre` (VARCHAR(200), NOT NULL) - Nombre del contacto
- `email` (VARCHAR(100)) - Email para conversaciones
- `whatsapp` (VARCHAR(20)) - Número de WhatsApp para conversaciones
- `telefono` (VARCHAR(20)) - Teléfono adicional
- `proyecto` (VARCHAR(200)) - Proyecto asociado
- `cargo` (VARCHAR(100)) - Cargo/posición del contacto
- `tipo` (ENUM: 'proveedor' | 'colaborador') - Tipo de contacto
- `proveedor_id` (INTEGER, FK -> proveedores.id) - Relación con proveedor (opcional)
- `notas` (TEXT) - Notas adicionales
- `activo` (BOOLEAN, DEFAULT TRUE)
- `fecha_registro` (TIMESTAMP)
- `fecha_actualizacion` (TIMESTAMP)

**Índices:**
- `idx_contactos_nombre` - Búsqueda rápida por nombre
- `idx_contactos_email` - Búsqueda rápida por email
- `idx_contactos_tipo` - Filtrado por tipo
- `idx_contactos_proveedor` - JOINs rápidos con proveedores
- `idx_contactos_activo` - Filtrado por estado activo
- `idx_contactos_proyecto` - Filtrado por proyecto

**Migración:** `migrations/create_contactos_table.sql`

---

## 🔧 BACKEND

### Modelo: `models/contacto.py`

- Clase `Contacto` con todos los campos
- Enum `TipoContacto` (PROVEEDOR, COLABORADOR)
- Relación con `Proveedor` (opcional)
- Método `to_dict()` para serialización

### Servicio: `modules/crm/contactos.py`

**Métodos disponibles:**
- `listar_contactos()` - Lista con filtros (tipo, proveedor, proyecto, búsqueda)
- `obtener_contacto()` - Obtiene un contacto por ID
- `crear_contacto()` - Crea un nuevo contacto
- `actualizar_contacto()` - Actualiza un contacto existente
- `eliminar_contacto()` - Marca como inactivo
- `enviar_mensaje_email()` - Envía email al contacto
- `enviar_mensaje_whatsapp()` - Envía WhatsApp al contacto

### Rutas API: `routes/crm_routes.py`

**Endpoints:**

1. **GET `/api/crm/contactos`** - Lista contactos
   - Query params: `tipo`, `proveedor_id`, `proyecto`, `activo`, `busqueda`, `skip`, `limit`

2. **POST `/api/crm/contactos`** - Crea contacto
   - Body: `nombre`, `email`, `whatsapp`, `telefono`, `proyecto`, `cargo`, `tipo`, `proveedor_id`, `notas`

3. **GET `/api/crm/contactos/<id>`** - Obtiene contacto por ID

4. **PUT `/api/crm/contactos/<id>`** - Actualiza contacto

5. **DELETE `/api/crm/contactos/<id>`** - Elimina contacto (marca como inactivo)

6. **POST `/api/crm/contactos/<id>/email`** - Envía email
   - Body: `asunto`, `contenido`

7. **POST `/api/crm/contactos/<id>/whatsapp`** - Envía WhatsApp
   - Body: `mensaje`

---

## 🎨 FRONTEND

### Componentes

1. **`frontend/src/pages/Contactos.jsx`** - Página principal
   - Lista de contactos con filtros
   - Panel de detalle del contacto seleccionado
   - Funcionalidad de conversación (Email y WhatsApp)
   - CRUD completo

2. **`frontend/src/components/ContactoForm.jsx`** - Formulario de contacto
   - Campos: nombre, tipo, email, whatsapp, teléfono, proyecto, cargo, proveedor (opcional), notas
   - Validación de campos requeridos
   - Select de proveedores cuando tipo es "proveedor"

### Características del Frontend

- ✅ Filtros por tipo (Proveedor/Colaborador)
- ✅ Filtros por proyecto
- ✅ Búsqueda por nombre, email, proyecto, cargo
- ✅ Envío de emails directamente desde la interfaz
- ✅ Envío de WhatsApp directamente desde la interfaz
- ✅ Vista de detalle del contacto
- ✅ CRUD completo (Crear, Leer, Actualizar, Eliminar)

### Rutas

- **Ruta:** `/contactos`
- **Menú:** CRM → Contactos
- **Icono:** Users

---

## 💬 FUNCIONALIDAD DE CONVERSACIÓN

### Email

- **Endpoint:** `POST /api/crm/contactos/<id>/email`
- **Campos requeridos:** `asunto`, `contenido`
- **Integración:** Usa `email_service` (SendGrid o Gmail SMTP)
- **Formato:** HTML con estilo profesional

### WhatsApp

- **Endpoint:** `POST /api/crm/contactos/<id>/whatsapp`
- **Campos requeridos:** `mensaje`
- **Integración:** Usa `whatsapp_service` (WhatsApp Business API)
- **Validación:** Limpia número de teléfono automáticamente

---

## 📋 CARACTERÍSTICAS PRINCIPALES

### Tipos de Contacto

1. **Proveedor**
   - Puede estar asociado a un proveedor existente
   - Campo `proveedor_id` opcional
   - Útil para gestionar múltiples contactos por proveedor

2. **Colaborador**
   - Contactos internos del equipo
   - No requiere proveedor asociado
   - Útil para gestión de personal

### Campos Especiales

- **Proyecto:** Permite agrupar contactos por proyecto
- **Cargo:** Posición del contacto (ej: "Gerente de Compras", "Chef Ejecutivo")
- **Email:** Requerido para envío de emails
- **WhatsApp:** Requerido para envío de mensajes WhatsApp

---

## 🔄 INTEGRACIÓN CON OTROS MÓDULOS

### Proveedores

- Los contactos pueden estar asociados a proveedores
- Al seleccionar tipo "proveedor", aparece selector de proveedores
- Relación opcional (puede haber contactos sin proveedor)

### Notificaciones

- Usa el servicio de email (`modules/crm/notificaciones/email.py`)
- Usa el servicio de WhatsApp (`modules/crm/notificaciones/whatsapp.py`)
- Requiere configuración previa de estos servicios

---

## 📝 PASOS PARA USAR

### 1. Ejecutar Migración

```sql
-- Ejecutar el archivo de migración
\i migrations/create_contactos_table.sql
```

O ejecutar manualmente el SQL en `migrations/create_contactos_table.sql`

### 2. Configurar Servicios de Comunicación

- **Email:** Configurar Gmail SMTP o SendGrid (ver módulo de Configuración)
- **WhatsApp:** Configurar WhatsApp Business API (ver módulo de Configuración)

### 3. Usar en la Interfaz

1. Ir a **CRM → Contactos**
2. Click en **"Nuevo Contacto"**
3. Completar formulario:
   - Nombre (requerido)
   - Tipo (Proveedor/Colaborador)
   - Email (para conversaciones por email)
   - WhatsApp (para conversaciones por WhatsApp)
   - Proyecto (opcional)
   - Cargo (opcional)
   - Proveedor asociado (solo si tipo es Proveedor)
4. Guardar contacto
5. Seleccionar contacto de la lista
6. Usar botones **"Enviar Email"** o **"Enviar WhatsApp"** para conversar

---

## ✅ VALIDACIONES

### Backend

- Nombre es requerido
- Tipo debe ser 'proveedor' o 'colaborador'
- Si se proporciona `proveedor_id`, el proveedor debe existir
- Email válido (formato)
- WhatsApp limpia automáticamente caracteres no numéricos

### Frontend

- Validación de campos requeridos
- Validación de formato de email
- Validación de mensajes antes de enviar
- Mensajes de error claros

---

## 🎯 CASOS DE USO

1. **Gestionar contactos de proveedores**
   - Crear múltiples contactos por proveedor
   - Asignar proyectos específicos
   - Comunicarse directamente por email o WhatsApp

2. **Gestionar colaboradores**
   - Registrar colaboradores internos
   - Asignar proyectos y cargos
   - Mantener comunicación directa

3. **Comunicación rápida**
   - Enviar emails desde la interfaz
   - Enviar mensajes WhatsApp desde la interfaz
   - Historial de comunicaciones (futuro)

---

## 🚀 PRÓXIMAS MEJORAS SUGERIDAS

1. Historial de conversaciones (tabla `conversaciones_contactos`)
2. Plantillas de mensajes
3. Programación de mensajes
4. Notificaciones de respuestas
5. Integración con calendario para recordatorios
6. Exportación de contactos (CSV, Excel)

---

**Fecha de Implementación:** 2026-01-30
**Versión:** 1.0
**Estado:** ✅ Completo y Funcional
