# Pixicon

Convert square images into **pixelated SVG icons** (crisp rects, nearest-neighbor resize).

Cross-platform desktop app for **Windows**, **Linux**, and **macOS**.

**Website:** [gixx.github.io/img2svg-icon-converter](https://gixx.github.io/img2svg-icon-converter/)

## Standalone builds (no Python required)

PyInstaller produces a self-contained app folder. End users do **not** need Python or pip.

| Platform | Artifact | How to run |
|----------|----------|------------|
| Windows x64 | `Pixicon-windows-x64.zip` → `Pixicon/Pixicon.exe` | Double-click the exe |
| Linux x64 | `Pixicon-linux-x64.tar.gz` → `Pixicon/Pixicon` | `./Pixicon/Pixicon` |
| macOS Intel | `Pixicon-macos-x64.zip` → `Pixicon.app` | Open the app |
| macOS Apple Silicon | `Pixicon-macos-arm64.zip` → `Pixicon.app` | Open the app |

### Build on this machine

```bash
# Windows (PowerShell)
./packaging/build.ps1

# Linux / macOS
chmod +x packaging/build.sh
./packaging/build.sh
```

Output lands in `dist/`.

### GitHub Release (all platforms)

Push a version tag — CI builds Windows, Linux, and both macOS architectures, then attaches the archives to a GitHub Release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Workflow: `.github/workflows/release.yml` (also runnable manually via **Actions → Release → Run workflow**).

> macOS apps are unsigned until notarization is set up; first open may need right-click → Open.

## Requirements (development)

- Python 3.10+
- Dependencies: Pillow, PySide6

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

## Run (from source)

```bash
python -m pixicon
# or
pixicon
```

## Rules (v1)

- Source images must be **square** and at most **512×512**
- Select **1–n files** (browse or drag & drop); no folder import
- Target sizes: 16, 24, 32, 48, 64, 128, 256
- Resize uses **nearest-neighbor** so pixels stay sharp

## Tests

```bash
pytest
```

## Website (GitHub Pages)

Static landing page lives in `website/`. Deploy workflow: `.github/workflows/pages.yml`.

In the GitHub repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**, then push to `main` (or run the workflow manually).

## License

MIT — see [LICENSE](LICENSE).
