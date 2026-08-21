# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for MarkSixAnalyzer."""
import sys
from pathlib import Path

block_cipher = None

package_dir = Path("marksix_analyzer")
datas = [(str(package_dir / "seed_data.csv"), "marksix_analyzer")]

_icon_name = "app.ico" if sys.platform == "win32" else "app.icns"
icon_path = _icon_name if Path(_icon_name).exists() else None

a = Analysis(
    ["run.py"],
    pathex=[str(Path.cwd())],
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
    console=False,
    icon=icon_path,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="MarkSixAnalyzer.app",
        icon=icon_path,
        bundle_identifier="com.garion.MarkSixAnalyzer",
    )
