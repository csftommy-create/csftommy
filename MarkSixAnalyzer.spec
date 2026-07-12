# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — build with: pyinstaller MarkSixAnalyzer.spec

Produces a single-file windowed executable (Windows) / .app bundle (macOS)
that bundles seed_data.csv. See README for platform notes.
"""
import sys
from pathlib import Path

block_cipher = None

# seed_data.csv lives inside the package; bundle it at the bundle root so
# config.resource_path("seed_data.csv") -> sys._MEIPASS/seed_data.csv resolves.
datas = [
    (str(Path("marksix_analyzer") / "seed_data.csv"), "."),
]

# Use an icon only if the file is actually present, so builds work out of the
# box before anyone supplies app.ico / app.icns.
_icon_name = "app.ico" if sys.platform == "win32" else "app.icns"
icon_path = _icon_name if Path(_icon_name).exists() else None

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["pyqtgraph"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MarkSixAnalyzer",
    debug=False,
    strip=False,
    upx=True,
    console=False,          # windowed
    icon=icon_path,
)

# macOS app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="MarkSixAnalyzer.app",
        icon=icon_path,
        bundle_identifier="com.garion.marksixanalyzer",
    )
