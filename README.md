# Smart Home Skill Hook

Esta API quedó reducida al mínimo para cumplir el requisito del profesor: una Skill de Alexa (o un Arduino que actúa como proxy) envía un token secreto y el `UUID` del dispositivo que representa la casa completa. El backend solo guarda el estado (encendido/apagado) asociado a ese UUID dentro de PostgreSQL.

## Flujo General
1. **Arranque** – `ensure_env_file()` garantiza que exista `.env` e incluye `ALEXA_SKILL_TOKEN`, host y credenciales de PostgreSQL.  
2. **Seeding** – `SeedService` ejecuta `DatabaseSeeder.run_all()` y crea la tabla `device_states`. Si ejecutes `scripts/migrate.py --reset` en desarrollo, la tabla se recrea.
3. **Base de datos automática** – si `POSTGRES_DB` no existe, el backend abre una conexión al `postgres` por defecto y la crea antes de continuar.
4. **Atención de solicitudes** – `src/routes.py` expone rutas protegidas con `X-Skill-Token`:
   - `GET /devices` lista todos los dispositivos registrados (normalmente solo habrá uno).
   - `GET /devices/{device_uuid}` devuelve el estado de un dispositivo puntual.
   - `GET /device-status?device_uuid=...` también devuelve el estado, pero usando query parameter (útil para clientes que no manejan path params).
   - `POST /devices` crea un dispositivo nuevo generando el `UUID` automáticamente. Puedes enviar `{ "status": true }` para dejarlo encendido desde el inicio.
   - `POST /devices/state` recibe `{ device_uuid, status }` y guarda el estado (inserta o actualiza según exista).
   - `POST /devices/toggle` recibe `{ device_uuid }` y alterna el estado actual (on/off) sin enviar un valor explícito.

Adicionalmente se mantienen `GET /health` y `GET /health/db` para monitoreo.

## Modelo de Datos
- **device_states** – Tabla con `device_uuid` (`UUID` y llave primaria), `status` (`BOOLEAN`) y `updated_at`. No hay usuarios ni relaciones; cada fila representa una casa o un nodo que Alexa puede encender/apagar.

## Seguridad para la Skill/Arduino
1. Copia `ALEXA_SKILL_TOKEN` del `.env` y configúralo en la Skill/firmware.  
2. Cada request debe incluir `X-Skill-Token: <valor>`; si falta o no coincide, el backend responde `401`.  
3. Para rotar el secreto, edita el `.env`, reinicia los contenedores y vuelve a flashear/enviar el nuevo token al Arduino/Alexa.

## Ejemplos de Uso

```bash
# Consultar salud
curl http://localhost:8000/health

# Listar dispositivos registrados
curl -H "X-Skill-Token: <TOKEN>" http://localhost:8000/devices

# Consultar un UUID específico
curl -H "X-Skill-Token: <TOKEN>" http://localhost:8000/devices/<UUID>

# O usando query param
curl -H "X-Skill-Token: <TOKEN>" "http://localhost:8000/device-status?device_uuid=<UUID>"

# Crear un dispositivo nuevo (la API genera el UUID)
curl -X POST http://localhost:8000/devices \
     -H "Content-Type: application/json" \
     -H "X-Skill-Token: <TOKEN>" \
     -d '{"status": true}'

# Actualizar el estado (enciende la casa completa)
curl -X POST http://localhost:8000/devices/state \
     -H "Content-Type: application/json" \
     -H "X-Skill-Token: <TOKEN>" \
     -d '{"device_uuid": "<UUID>", "status": true}'

# Alternar el estado sin saber si está on/off
curl -X POST http://localhost:8000/devices/toggle \
     -H "Content-Type: application/json" \
     -H "X-Skill-Token: <TOKEN>" \
     -d '{"device_uuid": "<UUID>"}'
```

Las respuestas devuelven:

```json
{
  "device_uuid": "5f80e8fe-9a58-41c8-922c-81bd01ef15a5",
  "status": "on",
  "last_updated": "2025-11-15T18:10:32.456231+00:00"
}
```

## Dependencias Relevantes
- **FastAPI / Uvicorn** – API asíncrona y servidor ASGI.
- **psycopg** – Driver para PostgreSQL.

No se manejan contraseñas ni tokens por usuario; la Skill actúa como único cliente autorizado.
