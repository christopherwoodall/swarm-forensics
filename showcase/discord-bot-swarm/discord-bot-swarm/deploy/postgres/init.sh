#!/bin/sh
set -eu
: "${SWARM_DB_PASSWORD:?Set the application database password}"
psql --no-psqlrc --set=ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres --set=app_password="$SWARM_DB_PASSWORD" <<'SQL'
CREATE ROLE swarm LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION PASSWORD :'app_password';
CREATE DATABASE discord_bot_swarm OWNER swarm;
REVOKE ALL ON DATABASE discord_bot_swarm FROM PUBLIC;
REVOKE CONNECT ON DATABASE postgres FROM PUBLIC;
\connect discord_bot_swarm
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO swarm;
SQL
