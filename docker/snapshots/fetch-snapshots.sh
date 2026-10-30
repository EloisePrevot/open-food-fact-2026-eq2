#!/bin/sh
set -u

for file in recipes.snapshot ingredients.snapshot mongo.archive.gz postgres.dump; do
  target="/snapshots/$file"
  if [ -f "$target" ]; then
    echo "$file : déjà téléchargé"
    continue
  fi
  echo "$file : téléchargement depuis $SNAPSHOTS_URL"
  if curl --fail --location --retry 3 --silent --show-error --output "$target.part" "$SNAPSHOTS_URL/$file"; then
    mv "$target.part" "$target"
  else
    rm -f "$target.part"
    echo "$file : non disponible, le pipeline chargera ces données lui-même"
  fi
done
