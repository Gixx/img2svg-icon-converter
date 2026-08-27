# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Pixicon (Windows / Linux / macOS)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"

block_cipher = None

datas = [
    (str(ASSETS / "pixicon-app-icon.png"), "assets"),
]

icon_file = ASSETS / "pixicon.ico"
if sys.platform == "darwin":
    icon_file = ASSETS / "pixicon-app-icon.png"

a = Analysis(
    [str(SRC / "pixicon" / "__main__.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# onedir: self-contained folder (reliable for Qt). Zip/tar for distribution.
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Pixicon",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_file.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Pixicon",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Pixicon.app",
        icon=str(icon_file) if icon_file.exists() else None,
        bundle_identifier="app.pixicon.desktop",
        info_plist={
            "CFBundleName": "Pixicon",
            "CFBundleDisplayName": "Pixicon",
            "CFBundleShortVersionString": "0.1.0",
            "NSHighResolutionCapable": True,
        },
    )
