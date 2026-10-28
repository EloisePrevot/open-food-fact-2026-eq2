#!/bin/sh
set -eu

set --
for collection in recipes ingredients; do
  snapshot="/snapshots/$collection.snapshot"
  if [ -f "$snapshot" ] && [ ! -d "/qdrant/storage/collections/$collection" ]; then
    echo "$collection : restauration depuis $snapshot"
    set -- "$@" --snapshot "$snapshot:$collection"
  fi
done

exec ./entrypoint.sh "$@"
