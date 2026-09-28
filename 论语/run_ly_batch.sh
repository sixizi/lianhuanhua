#!/bin/bash
# run_ly_batch.sh - 论语十回串行批量驱动（生成+合成）
cd "$(dirname "$0")/.."
for d in 论语/*/; do
  echo "======== $d ========"
  python3 "$d/gen_batch.py" 2>&1
done
echo "LY-BATCH-ALL-DONE"
