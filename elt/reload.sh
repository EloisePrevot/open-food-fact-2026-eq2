#!/bin/sh
# Recharge MongoDB et Qdrant depuis PostgreSQL, même si leur état de chargement est à jour.
# docker compose exec backend sh /app/elt/reload.sh
set -eu
cd "$(dirname "$0")"
python="${ELT_PYTHON:-python}"
limit="${ELT_LIMITE:-0}"
"$python" -m load --load-raw all
"$python" -m load --load-mongo --limit "$limit"
"$python" -m load --load-qdrant --limit "$limit"
