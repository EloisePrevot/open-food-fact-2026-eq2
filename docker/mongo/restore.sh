#!/bin/sh
set -eu

archive=/snapshots/mongo.archive.gz

if [ ! -f "$archive" ]; then
  echo "MongoDB : aucun dump disponible, le pipeline remplira la base"
  exit 0
fi

recipes=$(mongosh "$MONGODB_URI" --quiet --eval "db.getSiblingDB('$MONGODB_DATABASE').recipes.estimatedDocumentCount()")
if [ "$recipes" != "0" ]; then
  echo "MongoDB : base déjà remplie, restauration ignorée"
  exit 0
fi

echo "MongoDB : restauration depuis $archive"
mongorestore --uri="$MONGODB_URI" --gzip --archive="$archive" --nsInclude="$MONGODB_DATABASE.*"
