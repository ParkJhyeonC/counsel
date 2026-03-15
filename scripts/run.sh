#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] python3를 찾을 수 없습니다. Python 3.10+ 설치 후 다시 시도하세요."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[INFO] 가상환경 생성: $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r "$ROOT_DIR/requirements.txt"

export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

cd "$ROOT_DIR"
python -c "from app import init_db; init_db(); print('[INFO] DB 초기화 확인 완료')"
python app.py
