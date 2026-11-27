#!/usr/bin/env bash
set -euo pipefail

MINERU_DIR="${MINERU_DIR:-/e/minerU/MinerU}"
PY="${MINERU_PYTHON:-python}"
EXTRAS="${MINERU_EXTRAS:-pipeline}"
MIRROR="${MINERU_PIP_MIRROR:-https://mirrors.aliyun.com/pypi/simple}"

cd "$MINERU_DIR"
echo "==> MinerU source: $MINERU_DIR"
echo "==> Python: $PY"

if [ -d venv ]; then
  STAMP="$(date +%Y%m%d%H%M%S)"
  echo "==> Renaming existing venv to venv.broken.$STAMP"
  mv venv "venv.broken.$STAMP"
fi

echo "==> Creating venv"
"$PY" -m venv venv

VENV_PY="$MINERU_DIR/venv/Scripts/python.exe"
if [ ! -f "$VENV_PY" ]; then
  VENV_PY="$MINERU_DIR/venv/bin/python"
fi
if [ ! -f "$VENV_PY" ]; then
  echo "ERROR: venv interpreter was not created" >&2
  exit 1
fi

echo "==> Upgrading pip"
"$VENV_PY" -m pip install --upgrade pip -i "$MIRROR"

echo "==> Installing mineru[$EXTRAS] from source"
"$VENV_PY" -m pip install -e ".[$EXTRAS]" -i "$MIRROR"

echo "==> Downloading pipeline models from ModelScope"
"$VENV_PY" -m mineru.cli.models_download -s modelscope -m pipeline

echo "==> Setup complete. Re-run check_env.py to verify."
