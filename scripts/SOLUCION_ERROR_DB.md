# Solución: Error de Autenticación PostgreSQL

## 🔴 Problema

```
FATAL: la autentificaci�n password fall� para el usuario �postgres�
```

Este error indica que las credenciales de PostgreSQL en tu archivo `.env` son incorrectas.

## ✅ Solución Paso a Paso

### Paso 1: Verificar que PostgreSQL esté corriendo

Abre PowerShell y ejecuta:

```powershell
# Verificar si PostgreSQL está corriendo
Get-Service -Name postgresql*

# O si usas pg_ctl:
# pg_ctl status -D "C:\Program Files\PostgreSQL\XX\data"
```

Si no está corriendo, inícialo:

```powershell
# Iniciar servicio PostgreSQL
Start-Service postgresql-x64-XX  # Reemplaza XX con tu versión
```

### Paso 2: Verificar tu archivo `.env`

Abre el archivo `.env` en la raíz del proyecto y verifica estas variables:

```env
# Opción 1: Usar DATABASE_URL (recomendado)
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_bd

# Opción 2: Usar variables individuales
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_restaurantes
DB_USER=postgres
DB_PASSWORD=tu_contraseña_aqui
```

### Paso 3: Verificar/Cambiar la contraseña de PostgreSQL

#### Opción A: Si conoces la contraseña actual

1. Conéctate a PostgreSQL usando psql:

```powershell
# Conectarte como usuario postgres
psql -U postgres -d postgres
```

2. Si te pide contraseña y la conoces, ingrésala.

3. Si no conoces la contraseña, ve a la Opción B.

#### Opción B: Si NO conoces la contraseña

1. **En Windows, edita el archivo `pg_hba.conf`:**

   Ubicación típica:
   ```
   C:\Program Files\PostgreSQL\XX\data\pg_hba.conf
   ```

2. **Cambia la línea de autenticación:**

   Busca esta línea:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   ```

   Cámbiala temporalmente a:
   ```
   host    all             all             127.0.0.1/32            trust
   ```

3. **Reinicia PostgreSQL:**

   ```powershell
   Restart-Service postgresql-x64-XX
   ```

4. **Conéctate sin contraseña y cambia la contraseña:**

   ```powershell
   psql -U postgres -d postgres
   ```

   Luego en psql:
   ```sql
   ALTER USER postgres WITH PASSWORD 'nueva_contraseña_segura';
   \q
   ```

5. **Vuelve a cambiar `pg_hba.conf` a `scram-sha-256`** y reinicia PostgreSQL.

6. **Actualiza tu archivo `.env`** con la nueva contraseña.

### Paso 4: Verificar la conexión

Prueba conectarte manualmente:

```powershell
psql -U postgres -d erp_restaurantes -h localhost
```

Si funciona, el problema está resuelto.

### Paso 5: Ejecutar el script nuevamente

```powershell
python scripts/init_items.py
```

## 🔧 Configuración Recomendada para `.env`

```env
# Base de datos PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_restaurantes
DB_USER=postgres
DB_PASSWORD=tu_contraseña_segura_aqui

# O usar DATABASE_URL directamente:
# DATABASE_URL=postgresql+psycopg://postgres:tu_contraseña@localhost:5432/erp_restaurantes
```

## ⚠️ Notas Importantes

1. **Nunca subas tu archivo `.env` a Git** (ya está en `.gitignore`)

2. **Si usas Render o otro servicio cloud**, usa la `DATABASE_URL` que te proporcionan.

3. **Para desarrollo local**, asegúrate de que:
   - PostgreSQL esté instalado y corriendo
   - El usuario `postgres` exista
   - La base de datos `erp_restaurantes` exista (o el nombre que uses)

4. **Crear la base de datos si no existe:**

   ```powershell
   psql -U postgres
   ```

   Luego:
   ```sql
   CREATE DATABASE erp_restaurantes;
   \q
   ```

## 🆘 Si el problema persiste

1. Verifica que PostgreSQL esté escuchando en el puerto 5432:
   ```powershell
   netstat -an | findstr 5432
   ```

2. Verifica el firewall de Windows no esté bloqueando PostgreSQL.

3. Intenta conectarte desde otro cliente (pgAdmin, DBeaver) para verificar las credenciales.

4. Revisa los logs de PostgreSQL:
   ```
   C:\Program Files\PostgreSQL\XX\data\log\
   ```
