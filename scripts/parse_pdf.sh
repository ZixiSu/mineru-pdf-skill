#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: parse_pdf.sh <input_pdf_or_dir> <output_dir> [backend]" >&2
  exit 2
fi

INPUT="$1"
OUTPUT="${2:-./mineru_output}"
BACKEND="${3:-pipeline}"

MINERU_DIR="${MINERU_DIR:-/e/minerU/MinerU}"
cd "$MINERU_DIR"

VENV_PY="$MINERU_DIR/venv/Scripts/python.exe"
if [ ! -f "$VENV_PY" ]; then
  VENV_PY="$MINERU_DIR/venv/bin/python"
fi
if [ ! -f "$VENV_PY" ]; then
  echo "ERROR: venv not ready. Run setup_env.sh first." >&2
  exit 1
fi

CLI="$MINERU_DIR/venv/Scripts/mineru.exe"
if [ ! -f "$CLI" ]; then
  CLI="$MINERU_DIR/venv/bin/mineru"
fi

SOURCE="${MINERU_MODEL_SOURCE:-}"
if [ -z "$SOURCE" ]; then
  if [ -f "$HOME/mineru.json" ]; then
    SOURCE="local"
  else
    SOURCE="modelscope"
  fi
fi

mkdir -p "$OUTPUT"

echo "==> Parsing: $INPUT"
echo "==> Output:  $OUTPUT"
echo "==> Backend: $BACKEND (device cpu), model source: $SOURCE"

if [ -x "$CLI" ]; then
  "$CLI" -p "$INPUT" -o "$OUTPUT" -b "$BACKEND" -d cpu --source "$SOURCE"
else
  "$VENV_PY" -m mineru.cli.client -p "$INPUT" -o "$OUTPUT" -b "$BACKEND" -d cpu --source "$SOURCE"
fi

echo "==> Output files:"
find "$OUTPUT" -maxdepth 3 -type f | sort
