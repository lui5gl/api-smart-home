# Smart Home Skill Hook

La API quedó reducida al mínimo: Alexa (o un Arduino) controla un único estado (`on/off`) que se persiste en un archivo JSON (`STATE_FILE_PATH`). No hay base de datos ni múltiples dispositivos.

## Flujo General
1. **Arranque** – `ensure_env_file()` crea `.env` con `ALEXA_SKILL_TOKEN` y `STATE_FILE_PATH`.  
2. **Estado persistente** – `DeviceService` lee/escribe un archivo con `{ "status": bool, "last_updated": iso }`. Por defecto se crea `device_state.json` en la raíz del proyecto.  
3. **Atención de solicitudes** – todas las rutas protegidas con `X-Skill-Token` viven en `src/routes.py`:
   - `GET /device-status` → devuelve el estado actual.
   - `POST /device-status` → recibe `{ "status": true|false }` y actualiza el archivo.
   - `POST /device-status/toggle` → alterna automáticamente el valor sin cuerpo.
4. `GET /health` sigue disponible para verificar que el servicio esté arriba.

## Seguridad para la Skill/Arduino
Solo necesitas apuntar las solicitudes HTTP a tu instancia (no hay headers de autenticación). Si cambias `STATE_FILE_PATH`, asegúrate de que la ruta sea accesible para el proceso.

## Ejemplos

```bash
# Healthcheck
curl http://localhost/health

# Consultar estado
curl http://localhost/device-status

# Fijar estado explícito
curl -X POST http://localhost/device-status \
     -H "Content-Type: application/json" \
     -d '{"status": true}'

# Alternar sin payload
curl -X POST http://localhost/device-status/toggle
```

Respuesta típica:

```json
{
  "status": "on",
  "last_updated": "2025-11-15T18:10:32.456231+00:00"
}
```

## Dependencias
- **FastAPI / Uvicorn** – Framework + servidor ASGI.

No hay migraciones, scripts ni tablas. Solo asegúrate de que la ruta definida en `STATE_FILE_PATH` sea accesible para el proceso.***
