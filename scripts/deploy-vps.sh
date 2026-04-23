#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_HOST="root@195.54.170.223"
REMOTE_PATH="/var/www/savinvestimobiliare.ro/"

rsync -az --delete \
  --exclude '.git/' \
  --exclude 'backups/' \
  --exclude '.npm-cache/' \
  --exclude '.DS_Store' \
  --exclude 'marketing/' \
  "$ROOT_DIR/" \
  "${REMOTE_HOST}:${REMOTE_PATH}"

echo "Deploy complete to ${REMOTE_HOST}:${REMOTE_PATH}"
