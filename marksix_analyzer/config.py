"""Application configuration: paths, constants, ball colors, prize tiers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from platformdirs import user_data_dir
except Exception:  # pragma: no cover - platformdirs should be installed
    def user_data_dir(appname: str, appauthor: str | None = None) -> str:
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", str(Path.home()))
            return str(Path(base) / appname)
        elif sys.platform == "darwin":
            return str(Path.home() / "Library" / "Application Support" / appname)
        return str(Path.home() / ".local" / "share" / appname)


APP_NAME = "UKLottoAnalyzer"
APP_NAME_ZH = "UKLotto數據分析器"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Garion"

# Bump when seed_data.csv changes so existing databases re-import the newer
# bundled history on next launch (idempotent upsert; saved picks are untouched).
SEED_VERSION = "2002-07-04..2025-12-28"

# Number domain
MIN_NUMBER = 1
MAX_NUMBER = 59
MAIN_COUNT = 6

# --- Paths -----------------------------------------------------------------
DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "marksix.db"


def resource_path(relative: str) -> Path:
    """Resolve a bundled resource path, honoring PyInstaller's _MEIPASS."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / relative
    # During dev the resource sits next to the package root.
    return Path(__file__).resolve().parent / relative


SEED_CSV_PATH = resource_path("seed_data.csv")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# --- HKJC official ball color mapping -------------------------------------
# Verify against HKJC site during deployment; source: spec section 5.1.
RED_NUMBERS = {1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46}
BLUE_NUMBERS = {3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48}
GREEN_NUMBERS = {5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49}

BALL_COLORS = {
    "red": "#d32f2f",
    "blue": "#1565c0",
    "green": "#2e7d32",
    "extra": "#616161",
}


# --- Dark theme palette (from the v2.0 design mockup) ----------------------
THEME = {
    "bg": "#0A0A0B",           # app background
    "panel": "#121214",        # card / panel background
    "panel_border": "#1F1F23",
    "surface": "#17171A",      # inputs, nested surfaces
    "surface_border": "#2A2A2E",
    "surface_alt": "#1A1A1E",
    "accent": "#FF6B1A",       # orange accent
    "accent_hover": "#FF8A45",
    "accent_press": "#C93F00",
    "accent_glow": "rgba(255,107,26,0.13)",
    "text": "#EDEDEF",         # primary text
    "text_dim": "#A8A8B0",     # secondary
    "text_muted": "#8A8A92",   # tertiary
    "text_faint": "#6E6E76",
    "warn_bg": "#211B0E",
    "warn_border": "#4A3B12",
    "warn_text": "#FFD84D",
}


def ball_color_name(n: int) -> str:
    """Return the HKJC color group name for a number (1-49)."""
    if n in RED_NUMBERS:
        return "red"
    if n in BLUE_NUMBERS:
        return "blue"
    if n in GREEN_NUMBERS:
        return "green"
    return "extra"


def ball_color_hex(n: int) -> str:
    return BALL_COLORS[ball_color_name(n)]


# --- Prize structure (spec section 6, tab 7) -------------------------------
# (main_match, extra_matched) -> prize tier key
PRIZE_TIERS = {
    (6, False): "prize_1",  # 頭獎
    (5, True): "prize_2",   # 二獎 5 + 特
    (5, False): "prize_3",  # 三獎
    (4, True): "prize_4",   # 四獎 4 + 特
    (4, False): "prize_5",  # 五獎
    (3, True): "prize_6",   # 六獎 3 + 特
    (3, False): "prize_7",  # 七獎
}


def prize_tier(main_match: int, extra_matched: bool) -> str | None:
    """Return prize tier key or None for a given match profile."""
    return PRIZE_TIERS.get((main_match, extra_matched))
