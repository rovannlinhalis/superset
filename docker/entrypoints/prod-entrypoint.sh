#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Production entrypoint for Superset.
# - Waits for the external PostgreSQL metadata DB to be reachable
# - Applies DB migrations
# - Creates the admin user (idempotent: skipped if it already exists)
# - Initializes default roles/permissions
# - Hands off to gunicorn via run-server.sh
#
set -euo pipefail

: "${DATABASE_HOST:?DATABASE_HOST is required}"
: "${DATABASE_PORT:=5432}"
: "${DATABASE_USER:?DATABASE_USER is required}"
: "${DATABASE_PASSWORD:?DATABASE_PASSWORD is required}"
: "${DATABASE_DB:?DATABASE_DB is required}"
: "${SUPERSET_SECRET_KEY:?SUPERSET_SECRET_KEY is required}"

echo "Waiting for PostgreSQL at ${DATABASE_HOST}:${DATABASE_PORT}..."
ATTEMPTS=0
MAX_ATTEMPTS="${DB_WAIT_MAX_ATTEMPTS:-60}"
until python -c "
import os, sys, psycopg2
try:
    kwargs = {
        'host': os.environ['DATABASE_HOST'],
        'port': os.environ.get('DATABASE_PORT', '5432'),
        'user': os.environ['DATABASE_USER'],
        'password': os.environ['DATABASE_PASSWORD'],
        'dbname': os.environ['DATABASE_DB'],
        'connect_timeout': 3,
    }
    sslmode = os.environ.get('DATABASE_SSL_MODE')
    if sslmode:
        kwargs['sslmode'] = sslmode
    psycopg2.connect(**kwargs).close()
except Exception as exc:
    sys.exit(str(exc))
"; do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ "${ATTEMPTS}" -ge "${MAX_ATTEMPTS}" ]; then
        echo "PostgreSQL still unreachable after ${MAX_ATTEMPTS} attempts. Aborting." >&2
        exit 1
    fi
    sleep 2
done
echo "PostgreSQL is reachable."

echo "Applying DB migrations..."
superset db upgrade

if [ "${SUPERSET_SKIP_ADMIN_CREATE:-false}" != "true" ]; then
    ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
    ADMIN_EMAIL="${ADMIN_EMAIL:-admin@superset.local}"
    ADMIN_FIRSTNAME="${ADMIN_FIRSTNAME:-Superset}"
    ADMIN_LASTNAME="${ADMIN_LASTNAME:-Admin}"
    if [ -z "${ADMIN_PASSWORD:-}" ]; then
        echo "ADMIN_PASSWORD not set; skipping admin user creation."
    else
        echo "Ensuring admin user '${ADMIN_USERNAME}' exists..."
        superset fab create-admin \
            --username "${ADMIN_USERNAME}" \
            --firstname "${ADMIN_FIRSTNAME}" \
            --lastname "${ADMIN_LASTNAME}" \
            --email "${ADMIN_EMAIL}" \
            --password "${ADMIN_PASSWORD}" || echo "Admin user already exists; continuing."
    fi
fi

echo "Initializing roles and permissions..."
superset init

echo "Starting gunicorn..."
exec /app/docker/entrypoints/run-server.sh
