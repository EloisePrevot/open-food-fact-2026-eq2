#!/bin/sh
set -eu

dump=/snapshots/postgres.dump
if [ ! -f "$dump" ]; then
  echo "PostgreSQL : aucun dump disponible, le pipeline remplira la base"
  exit 0
fi

present=$(psql "$POSTGRES_URI" --tuples-only --no-align --command "SELECT to_regclass('public.raw_artifacts') IS NOT NULL")
if [ "$present" = "t" ]; then
  echo "PostgreSQL : base déjà remplie, restauration ignorée"
  exit 0
fi

echo "PostgreSQL : restauration depuis $dump"
pg_restore --no-owner --no-privileges --exit-on-error --dbname="$POSTGRES_URI" "$dump"
