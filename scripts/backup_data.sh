#!/usr/bin/env sh
set -eu

SOURCE_DIR="${DATA_DIR:-data}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="${BACKUP_DIR}/graphrag-benchmark-data-${STAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"
tar \
  --exclude='.env' \
  --exclude='.env.*' \
  -czf "$TARGET" \
  "$SOURCE_DIR/raw" \
  "$SOURCE_DIR/processed" \
  "$SOURCE_DIR/embeddings" \
  "$SOURCE_DIR/results" \
  "$SOURCE_DIR/graph" \
  "$SOURCE_DIR/chroma"

echo "Backup written to $TARGET"
