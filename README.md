# Smart Home API – Functional Overview

This backend coordinates three things: user accounts, smart devices, and the relationships between them. Everything is exposed through a FastAPI HTTP surface, and all persistence happens in PostgreSQL via a thin service layer that validates ownership rules before touching the database.

## High-Level Flow
1. **Environment bootstrap** – `ensure_env_file()` (called at startup in `src/app.py`) guarantees there is a `.env` with strong secrets. Values in that file drive both containers and the application code.
2. **Schema management** – `SeedService` invokes `DatabaseSeeder.run_all()` on every boot. In `development` it first drops the managed tables, ensuring each run starts fresh; in `production` it only creates missing tables.
3. **Request handling** – `src/routes.py` wires HTTP routes to specific services: `HealthService`, `DeviceService`, and `UserService`. Routes only transform payloads; all business rules live in those services.

## Data Model
- **users** – Represents an account with `name`, unique `username`, and a bcrypt-hashed `password`. `last_entry`, `created_at`, and `updated_at` keep audit info.
- **devices** – Represents a physical item. Each device has a `name` (friendly label), a unique `serial_number`, and timestamps.
- **account_devices** – Join table linking a user to a device, plus the device `status` (`on/off`). A unique constraint on `(device_id, user_id)` prevents duplicate associations and acts as the authorization oracle for any device action.

## Service Responsibilities
### HealthService (`src/services/health.py`)
Runs `SELECT 1` to confirm database health. Used by `/health/db`.

### UserService (`src/services/users.py`)
`register()` checks username uniqueness, hashes the incoming password, and inserts the record. No admin defaults are auto-created—real accounts must be registered through the API or scripts.

### DeviceService (`src/services/devices.py`)
- `list_user_devices(username)` returns only the devices tied to that user, translating boolean status to `"on"/"off"` and exposing last-updated timestamps.
- `add_device()` either creates a brand-new hardware row or reuses an existing one (matched by serial/name), then ensures the `account_devices` link exists and sets its status.
- `update_status()` flips the smart device on/off but only after verifying the `(user, device)` relationship exists; otherwise it returns `404`.
- `rename_device()` updates the friendly name as long as the caller owns the device and the new name is unique.

### DatabaseSeeder (`src/database/seeder.py`)
- `reset_schema()` drops `account_devices`, `devices`, and `users`. Triggered automatically whenever `ENV=development`.
- `seed_devices()`, `seed_users()`, `seed_account_devices()` only create tables; no fake rows are inserted so production data always originates from real events.

## Request/Response Summary

| Method | Path | Purpose | Key Rules |
|--------|------|---------|-----------|
| GET | `/health` | Liveness probe. | Returns `{ "status": "ok" }`. |
| GET | `/health/db` | Database readiness. | Executes `SELECT 1`; 500 on failure. |
| POST | `/users/register` | Adds a new account. | Requires `{ name, username, password }`; password stored as bcrypt hash. |
| GET | `/devices` | Lists user devices. | `username` query param; returns only devices linked via `account_devices`. |
| POST | `/devices` | Adds or links a device. | Payload `{ username, device_name, serial_number, status? }`; prevents duplicate serials and maintains association row. |
| POST | `/devices/status` | Toggles device power. | Payload `{ username, device_name, status }`; fails with 404 if user is not linked. |
| PATCH | `/devices/name` | Renames a device. | Payload `{ username, current_name, new_name }`; ensures uniqueness and ownership. |

## Typical Lifecycle
1. **Register** – Client calls `/users/register` to create an account.
2. **Add device** – Client calls `/devices` with serial/name to register hardware against that account.
3. **Control device** – Client toggles `/devices/status` as needed and optionally renames the device via `/devices/name`.
4. **Monitoring** – `/devices` fetches the latest state; `/health` & `/health/db` feed monitoring dashboards.

## Supporting Scripts & Components
- `scripts/migrate.py` – CLI wrapper around the seeder. Useful in CI/CD to recreate the schema (`ENV`-aware) or to force a reset via `--reset` when not already in development mode.
- `Dockerfile`/`docker-compose.yml` – Provide the runtime, binding the source tree into the container so the API always runs off the host files.
- `requirements.txt` – Minimal dependency surface: FastAPI/Uvicorn, psycopg, passlib for bcrypt hashing.

## Security Considerations
- Passwords are hashed with bcrypt (via `passlib`). There is no plaintext storage.
- Device mutations always confirm user ownership in SQL, preventing one user from controlling another user’s device.
- No default accounts or devices are injected; anything in the database was created through the API or explicit migrations.

## Observability Hooks
- HTTP-level `/health` and database-level `/health/db` endpoints can be wired into container healthchecks or external monitors.
- Uvicorn logs provide request traces, and startup logs warn if a new `.env` was auto-generated so operators can capture the generated secrets.

## Extensibility Ideas
- Add authentication tokens atop the existing user system.
- Expand `DeviceService` with room/zone grouping or telemetry history tables.
- Replace the simple seeder with a migration framework (Alembic/Flyway) once schema evolution becomes more complex.
