#!/bin/sh
set -eu

mongodump --uri="$MONGODB_URI" --db="$MONGODB_DATABASE" --gzip --archive=/export/mongo.archive.gz
echo "MongoDB : dump écrit dans elt/snapshots/mongo.archive.gz"
