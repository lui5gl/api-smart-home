# Smart Home API – Descripción Funcional

Este backend coordina tres piezas: cuentas de usuario, dispositivos inteligentes y las relaciones entre ambos. Todo se expone mediante FastAPI, mientras que la persistencia vive en PostgreSQL a través de una capa de servicios que valida la propiedad antes de ejecutar cualquier operación.

## Flujo General
1. **Arranque del entorno** – `ensure_env_file()` (ejecutado al iniciar `src/app.py`) garantiza la existencia de un `.env` con secretos seguros. Esos valores alimentan a los contenedores y al código.
2. **Gestión del esquema** – `SeedService` llama a `DatabaseSeeder.run_all()` en cada arranque. Si `ENV=development`, primero elimina las tablas gestionadas para empezar desde cero; en `production` solo crea las faltantes.
3. **Atención de solicitudes** – `src/routes.py` conecta los endpoints HTTP con `HealthService`, `DeviceService` y `UserService`. Las rutas solo validan/parsean datos; las reglas viven en los servicios.

## Modelo de Datos
- **users** – Cuenta de usuario con `name`, `username` único y `password` en bcrypt. Campos `last_entry`, `created_at` y `updated_at` guardan auditoría.
- **devices** – Dispositivo físico con `device_uuid` (identificador estable), `name` (alias amigable), `serial_number` único y marcas de tiempo.
- **account_devices** – Tabla puente que une usuarios y dispositivos, añade `status` (`on/off`) y obliga a unicidad `(device_id, user_id)` para validar propiedad.

## Servicios Principales
### HealthService (`src/services/health.py`)
Ejecuta `SELECT 1` para confirmar la salud de la base. Respalda `/health/db`.

### UserService (`src/services/users.py`)
`register()` comprueba si el `username` existe, hashea la contraseña recibida y crea la fila. No se autogeneran cuentas; todas deben registrarse vía API o scripts.

### DeviceService (`src/services/devices.py`)
- `list_user_devices(username)` devuelve solo los dispositivos asociados, normalizando el estado a "on"/"off" y exponiendo `last_updated`.
- `add_device()` crea un hardware nuevo o reutiliza uno por serie/nombre, y asegura la relación en `account_devices` con el estado solicitado.
- `update_status()` enciende/apaga solo si el usuario posee el dispositivo; si no, responde `404`.
- `rename_device()` cambia el nombre amigable respetando propiedad y unicidad.

### DatabaseSeeder (`src/database/seeder.py`)
- `reset_schema()` elimina `account_devices`, `devices` y `users`; se ejecuta automáticamente cuando `ENV=development`.
- `seed_devices()`, `seed_users()` y `seed_account_devices()` únicamente crean las tablas; no insertan datos ficticios.

## Endpoints y Reglas

| Método | Ruta | Propósito | Reglas clave |
|--------|------|-----------|--------------|
| GET | `/health` | Verifica que la API esté viva. | Devuelve `{ "status": "ok" }`. |
| GET | `/health/db` | Comprueba conexión a PostgreSQL. | Ejecuta `SELECT 1`; responde 500 ante fallas. |
| POST | `/users/register` | Registra un usuario nuevo. | Requiere `{ name, username, password }`; guarda password en bcrypt. |
| GET | `/devices` | Lista los dispositivos de un usuario. | Parámetro `username`; retorna `{ uuid, name, serial_number, status, last_updated }` por cada uno; requiere `X-Skill-Token`. |
| GET | `/devices/status` | Consulta el estado de un dispositivo puntual. | Parámetros `username` y `device_uuid`; devuelve el mismo payload `{ uuid, name, serial_number, status, last_updated }`; responde 404 si no están asociados; requiere `X-Skill-Token`. |
| POST | `/devices` | Alta o asociación de dispositivo. | Payload `{ username, device_name, serial_number, status? }`; evita seriales duplicados; requiere `X-Skill-Token`. |
| POST | `/devices/status` | Enciende/apaga un dispositivo. | Payload `{ username, device_uuid, status }`; falla con 404 si no hay vínculo; requiere `X-Skill-Token`. |
| PATCH | `/devices/name` | Renombra el dispositivo. | Payload `{ username, device_uuid, new_name }`; exige propiedad y nombre único; requiere `X-Skill-Token`. |

## Ciclo Típico
1. **Registro** – Cliente llama a `/users/register` para crear cuenta.
2. **Alta de dispositivo** – Cliente envía `/devices` con serie/nombre para vincular hardware.
3. **Control** – Cliente usa `/devices/status` para encender/apagar y `/devices/name` para renombrar.
4. **Monitoreo** – `/devices` muestra el estado actual; `/health` y `/health/db` alimentan dashboards.

## Componentes de Apoyo
- `scripts/migrate.py` – Ejecuta la lógica del seeder. Útil en CI/CD para recrear el esquema (respeta `ENV`) o forzar `--reset` cuando no estamos en development.
- `Dockerfile` y `docker-compose.yml` – Definen la orquestación, montan el código del host en el contenedor y exponen el servicio en `8000`.
- `requirements.txt` – Dependencias esenciales: FastAPI/Uvicorn, psycopg y passlib (bcrypt).

## Consideraciones de Seguridad
- Las contraseñas se almacenan como hashes bcrypt; nunca se guardan en texto plano.
- Cada operación sobre dispositivos valida en SQL que el usuario realmente posee ese equipo.
- No se cargan cuentas ni dispositivos por defecto; cualquier dato existente proviene de acciones reales.
- Todas las rutas de control de dispositivos validan un encabezado `X-Skill-Token` que debe coincidir con `ALEXA_SKILL_TOKEN` en el `.env`; solo la Skill de Alexa o el Arduino deberían conocer ese secreto.

## Autenticación para Alexa/Arduino
1. `ensure_env_file()` genera `ALEXA_SKILL_TOKEN` si no existe. Copia ese valor para configurarlo en la Skill y en el Arduino (o lo que haga bridge con Alexa).
2. Toda llamada a `/devices` (GET/POST/PATCH) y `/devices/status` debe llevar `X-Skill-Token: <valor>`; si falta o no coincide, la API responde `401 Unauthorized`.
3. Para rotar el token, actualiza `ALEXA_SKILL_TOKEN` en el `.env`, reinicia el servicio y vuelve a desplegar/configurar los clientes.

## Observabilidad
- `/health` y `/health/db` pueden usarse como healthchecks en Compose/Kubernetes.
- Los logs de Uvicorn registran cada petición y el arranque advierte cuando se genera un `.env` nuevo para resguardar los secretos.

## Siguientes Pasos Posibles
- Incorporar autenticación basada en tokens o sesiones.
- Agrupar dispositivos por habitaciones/zona o registrar historial de telemetría.
- Sustituir el seeder por un framework de migraciones (Alembic, Flyway) si el esquema crece en complejidad.
