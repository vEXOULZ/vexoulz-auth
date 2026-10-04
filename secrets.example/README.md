# secrets

Copy this directory to `secrets/` (gitignored) and replace each placeholder. One file per secret, named
like its variable in lowercase; compose mounts them at `/run/secrets/<name>`.

| File | What |
|---|---|
| `auth_database_url` | Postgres URL for the service and the migrate step. Its password is `auth_db_password` |
| `auth_db_password` | The `db` service's password. Read by Postgres only when it first creates the database |
| `auth_twitch_client_secret` | The Twitch application's client secret |
| `auth_token_key` | Fernet key encrypting stored Twitch tokens: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Changing it signs everyone out |
| `auth_clients` | The backends, as JSON (see `.env.example`) |

Mode 0400. The container reads them as its own user: `auth_db_password` must be readable by uid 70
(postgres in `postgres:17-alpine`), the rest by uid 10001 (`auth` in the image).
