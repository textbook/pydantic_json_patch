#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

COMMAND="${1:-check}"

if [[ "$#" -gt 1 ]]; then
  echo 'usage: ./bin/dev.sh [command]'
  exit 1
fi

uv_run () {
  uv --directory="$ROOT" run "$@"
}

check () {
  uv_run ty check
  uv_run ruff check
  uv_run ruff format --check
  uv_run coverage run --module pytest
  uv_run coverage report
}

ship () {
  check
  if [[ -z "$(git status --porcelain --untracked-files=no)" ]]; then
    echo 'ship it 🚢' && git push
  else
    echo 'all checks passed but repo state is not clean' && exit 1
  fi
}

case "$COMMAND" in
  check) check;;
  ship) ship;;
  *) echo "unsupported command: $COMMAND"; exit 1;;
esac
