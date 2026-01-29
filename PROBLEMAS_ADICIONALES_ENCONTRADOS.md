# ⚠️ PROBLEMAS ADICIONALES ENCONTRADOS

**Fecha:** 29 de Enero, 2026

---

## 🚨 PROBLEMAS CRÍTICOS EN MÓDULOS

### 1. Error `db.commit()` en Módulos (50+ instancias)

**Problema:** Los módulos usan `db.commit()` cuando deberían usar `db.session.commit()`.

**Ubicaciones encontradas:**
- `modules/logistica/pedidos_internos.py` - 3 instancias
- `modules/logistica/costos.py` - 3 instancias
- `modules/crm/tickets.py` - 4 instancias
- `modules/logistica/items.py` - 5 instancias
- `modules/logistica/inventario.py` - 1 instancia
- `modules/planificacion/programacion.py` - 2 instancias
- `modules/chat/chat_service.py` - 3 instancias
- `modules/planificacion/recetas.py` - 2 instancias
- `modules/logistica/facturas.py` - 6 instancias
- `modules/logistica/facturas_whatsapp.py` - 1 instancia
- `modules/crm/tickets_automaticos.py` - 6 instancias
- `modules/logistica/pedidos_automaticos.py` - 2 instancias
- `modules/logistica/pedidos.py` - 3 instancias
- `modules/crm/proveedores.py` - 4 instancias
- `modules/reportes/mermas.py` - 1 instancia
- `modules/reportes/charolas.py` - 1 instancia
- `modules/logistica/requerimientos.py` - 2 instancias
- `modules/contabilidad/centro_cuentas.py` - 1 instancia

**Total:** 50+ instancias

**Impacto:** Puede causar errores en tiempo de ejecución ya que `db` es una instancia de SQLAlchemy, no tiene método `commit()` directo.

---

### 2. Uso de `print()` en lugar de Logging Estructurado

**Problema:** Muchos módulos usan `print()` para logging en lugar de logging estructurado.

**Ubicaciones encontradas:**
- `modules/logistica/costos.py` - 2 instancias
- `modules/crm/tickets.py` - 4 instancias
- `modules/logistica/facturas.py` - 1 instancia
- `modules/logistica/facturas_whatsapp.py` - 3 instancias
- `modules/logistica/pedidos_automaticos.py` - 1 instancia
- `modules/logistica/pedidos.py` - 2 instancias
- `modules/crm/notificaciones/email.py` - 2 instancias
- `modules/crm/notificaciones/whatsapp.py` - 2 instancias

**Total:** 17+ instancias

**Impacto:** 
- No se pueden filtrar logs por nivel
- No se pueden enviar a sistemas de logging centralizados
- Dificulta debugging en producción

---

### 3. Manejo de Errores con `except:` Vacío

**Problema:** Algunos bloques `except:` están vacíos o solo tienen `pass`, ocultando errores.

**Ubicaciones encontradas:**
- `modules/logistica/facturas_whatsapp.py` - Varios `except:` vacíos

**Impacto:** Errores silenciosos que dificultan el debugging.

---

## 🔧 CORRECCIONES NECESARIAS

### Prioridad Crítica
1. ✅ Corregir todos los `db.commit()` → `db.session.commit()`
2. ✅ Reemplazar `print()` por logging estructurado
3. ✅ Mejorar manejo de errores con `except:` vacíos

### Prioridad Alta
4. ✅ Verificar `db.refresh()` también
5. ✅ Agregar logging estructurado consistente
6. ✅ Mejorar manejo de excepciones

---

## 📝 NOTA

Estos problemas están en los **módulos de servicios**, no en las rutas. Las rutas ya están corregidas, pero los servicios que llaman también necesitan corrección para garantizar consistencia completa.

---

**Fin del Reporte**
