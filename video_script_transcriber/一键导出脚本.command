#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"
source .venv/bin/activate

INPUT_FILE="${1:-$SCRIPT_DIR/urls.txt}"
OUTPUT_DIR="${2:-$SCRIPT_DIR/output_auto}"

python auto_export_pipeline.py \
  --input "$INPUT_FILE" \
  --output-dir "$OUTPUT_DIR" \
  --model tiny \
  --language zh
