#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Ошибка: не найден python3. Установите Python 3.11+ и повторите."
  exit 1
fi

PY_MINOR="$(python3 -c 'import sys; print(sys.version_info.minor)')"
if [ "$PY_MINOR" -lt 11 ]; then
  echo "Ошибка: нужен Python 3.11 или новее. Найден: $(python3 --version)"
  exit 1
fi

if [ ! -d .venv ]; then
  echo "Создаю .venv..."
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p data/backups cache logs

if ! command -v ollama >/dev/null 2>&1; then
  echo
  echo "Внимание: Ollama не найдена. Установите Ollama отдельно, затем выполните:"
  echo "  ollama pull qwen3:14b"
else
  if ! ollama list 2>/dev/null | awk '{print $1}' | grep -qx 'qwen3:14b'; then
    echo
    echo "Ollama найдена, но qwen3:14b пока не загружена. Выполните:"
    echo "  ollama pull qwen3:14b"
  fi
fi

echo
echo "Scribe установлен в: $ROOT"
echo "Запуск: ./run.sh"
