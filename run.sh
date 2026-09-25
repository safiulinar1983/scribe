#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [ ! -x .venv/bin/python ]; then
  echo "Окружение .venv не найдено. Сначала запустите ./setup.sh"
  exit 1
fi
exec .venv/bin/python agent.py "$@"
