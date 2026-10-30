#!/bin/sh
set -eu

pg_dump --format=custom --no-owner --no-privileges --dbname="$POSTGRES_SAMPLE_URI" --file=/export/postgres.dump
echo "PostgreSQL : dump de l'échantillon brut écrit dans elt/snapshots/postgres.dump"
