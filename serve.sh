#!/usr/bin/env bash
# Tailnet demo only: serve dist/ on PORT (default 8765). Build first: python3 build.py
set -euo pipefail
cd "$(dirname "$0")"
[ -f dist/index.html ] || { echo "serve: dist/index.html missing — run: python3 build.py" >&2; exit 1; }
exec python3 -m http.server "${PORT:-8765}" --directory dist
