#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: scripts/restore_data.sh path/to/backup.tar.gz" >&2
  exit 1
fi

mkdir -p data
tar -xzf "$1" -C .
echo "Restored data from $1"
