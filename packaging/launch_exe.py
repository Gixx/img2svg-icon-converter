"""Launch packaged Pixicon.exe (used by VS Code / Cursor F5)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "dist" / "Pixicon" / "Pixicon.exe"


def _stop_running() -> None:
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/IM", "Pixicon.exe"],
            check=False,
            capture_output=True,
        )
        time.sleep(0.3)


def main() -> int:
    if not EXE.is_file():
        print(f"Missing {EXE}. Run packaging/build.ps1 first.", file=sys.stderr)
        return 1
    _stop_running()
    print(f"Starting {EXE}")
    return subprocess.call([str(EXE)], cwd=str(EXE.parent))


if __name__ == "__main__":
    raise SystemExit(main())
