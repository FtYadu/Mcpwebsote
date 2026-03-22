#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_FILE="${ROOT_DIR}/.env"

if [[ -f "${TARGET_FILE}" ]]; then
  echo ".env already exists at ${TARGET_FILE}"
  exit 0
fi

cp "${ROOT_DIR}/.env.example" "${TARGET_FILE}"
echo "Created ${TARGET_FILE} from .env.example"
