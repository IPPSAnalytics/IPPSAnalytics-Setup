#!/bin/bash

ORG="IPPSAnalytics"
DEST="${1:-$HOME/Desktop/$ORG}"

# Check for gh CLI
if ! command -v gh &>/dev/null; then
  echo "Error: GitHub CLI (gh) is not installed."
  echo "Install it from https://cli.github.com/ then run: gh auth login"
  exit 1
fi

# Check for gh auth
if ! gh auth status &>/dev/null; then
  echo "Error: Not authenticated with GitHub CLI."
  echo "Run: gh auth login"
  exit 1
fi

mkdir -p "$DEST"
echo "Cloning all repos from '$ORG' into $DEST"
echo "======================================="

# Fetch all repo names (handles pagination automatically)
repos=$(gh repo list "$ORG" --limit 200 --json name --jq '.[].name')

if [ -z "$repos" ]; then
  echo "No repos found for org '$ORG'. Check org name and permissions."
  exit 1
fi

SUCCESS=0
SKIPPED=0
FAILED=0

while IFS= read -r repo; do
  target="$DEST/$repo"

  if [ -d "$target/.git" ]; then
    echo "~ $repo — already exists, skipping"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  output=$(gh repo clone "$ORG/$repo" "$target" 2>&1)
  status=$?

  if [ $status -eq 0 ]; then
    echo "✓ $repo"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "✗ $repo — FAILED"
    echo "  $output"
    FAILED=$((FAILED + 1))
  fi
done <<< "$repos"

echo "======================================="
echo "Done: $SUCCESS cloned, $SKIPPED skipped (already exists), $FAILED failed"
echo "Location: $DEST"
