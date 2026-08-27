#!/usr/bin/env bash
# Build standalone Pixicon for the current OS.
# Output: dist/Pixicon/ (Linux) or dist/Pixicon.app (macOS) + archive.
#
# Optional env:
#   PIXICON_ARTIFACT  - archive filename (overrides default per-OS name)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
else
  PY=python3
fi

"$PY" -m pip install -U pip
"$PY" -m pip install -e .
"$PY" -m pip install "pyinstaller>=6.3"
"$PY" -m PyInstaller --noconfirm --clean packaging/pixicon.spec

OS="$(uname -s)"
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64) ARCH_LABEL="x64" ;;
  arm64|aarch64) ARCH_LABEL="arm64" ;;
  *) ARCH_LABEL="$ARCH" ;;
esac

case "$OS" in
  Darwin)
    if [[ ! -d dist/Pixicon.app ]]; then
      echo "Build finished but dist/Pixicon.app missing" >&2
      exit 1
    fi
    ARTIFACT="${PIXICON_ARTIFACT:-Pixicon-macos-${ARCH_LABEL}.zip}"
    OUT="dist/${ARTIFACT}"
    rm -f "$OUT"
    ditto -c -k --sequesterRsrc --keepParent dist/Pixicon.app "$OUT"
    echo "OK  app: dist/Pixicon.app"
    echo "OK  zip: $OUT"
    ;;
  Linux)
    if [[ ! -x dist/Pixicon/Pixicon ]]; then
      echo "Build failed: dist/Pixicon/Pixicon not found" >&2
      exit 1
    fi
    ARTIFACT="${PIXICON_ARTIFACT:-Pixicon-linux-${ARCH_LABEL}.tar.gz}"
    OUT="dist/${ARTIFACT}"
    rm -f "$OUT"
    tar -C dist -czf "$OUT" Pixicon
    echo "OK  folder: dist/Pixicon"
    echo "OK  archive: $OUT"
    echo "Run: ./dist/Pixicon/Pixicon"
    ;;
  *)
    echo "Unsupported OS: $OS" >&2
    exit 1
    ;;
esac
