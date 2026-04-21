#!/bin/bash

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUCCESS=0
FAILED=0
SKIPPED=0

echo "Updating all repos in IPPSAnalytics..."
echo "======================================="

for dir in "$ROOT"/*/; do
  if [ ! -d "$dir/.git" ]; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  name=$(basename "$dir")
  branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null)
  output=$(git -C "$dir" pull 2>&1)
  status=$?

  if [ $status -eq 0 ]; then
    echo "✓ $name ($branch) — $output"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "✗ $name ($branch) — FAILED"
    echo "  $output"
    FAILED=$((FAILED + 1))
  fi
done

echo "======================================="
echo "Done: $SUCCESS updated, $FAILED failed, $SKIPPED skipped (not a git repo)"
