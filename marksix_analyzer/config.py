"""Application configuration: paths, constants, ball colors, prize tiers."""
from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from platformdirs import user_data_dir
except Exception:  # pragma: no cover
    def user_data_dir(appname: str, appauthor: str | None = None) -> str:
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", str(Path.home()))
            return str(Path(base) / appname)
        if sys.platform == "darwin":
            return str(Path.home() / "Library" / "Application Support" / appname)
        return str(Path.home() / ".local" / "share" / appname)


APP_NAME = "MarkSixAnalyzer"
APP_NAME_ZH = "Mark Six 數據分析器"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Garion"

SEED_VERSION = "2015-01-03..2026-08-08"

MIN_NUMBER = 1
MAX_NUMBER = 59
MAIN_COUNT = 6

DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DB_PATH = DATA_DIR / "marksix.db"


def resource_path(relative: str) -> Path:
    """Resolve a bundled resource path, including PyInstaller _MEIPASS."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / relative
    return Path(__file__).resolve().parent / relative


SEED_CSV_PATH = resource_path("seed_data.csv")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


WHITE_NUMBERS = {1, 2, 3, 4, 5, 6, 7, 8, 9}
BLUE_NUMBERS = {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}
PINK_NUMBERS = {20, 21, 22, 23, 24, 25, 26, 27, 28, 29}
GREEN_NUMBERS = {30, 31, 32, 33, 34, 35, 36, 37, 38, 39}
YELLOW_NUMBERS = {40, 41, 42, 43, 44, 45, 46, 47, 48, 49}
PURPLE_NUMBERS = {50, 51, 52, 53, 54, 55, 56, 57, 58, 59}

BALL_COLORS = {
    "white": "#ffffff",
    "blue": "#03a9f4",
    "pink": "#e91e63",
    "green": "#8bc34a",
    "yellow": "#ffd600",
    "purple": "#8e24aa",
    "extra": "#616161",
}

THEME = {
    "bg": "#0A0A0B", "panel": "#121214", "panel_border": "#1F1F23",
    "surface": "#17171A", "surface_border": "#2A2A2E", "surface_alt": "#1A1A1E",
    "accent": "#FF6B1A", "accent_hover": "#FF8A45", "accent_press": "#C93F00",
    "accent_glow": "rgba(255,107,26,0.13)", "text": "#EDEDEF", "text_dim": "#A8A8B0",
    "text_muted": "#8A8A92", "text_faint": "#6E6E76", "warn_bg": "#211B0E",
    "warn_border": "#4A3B12", "warn_text": "#FFD84D",
}


def ball_color_name(n: int) -> str:
    if n in WHITE_NUMBERS:
        return "white"
    if n in BLUE_NUMBERS:
        return "blue"
    if n in PINK_NUMBERS:
        return "pink"
    if n in GREEN_NUMBERS:
        return "green"
    if n in YELLOW_NUMBERS:
        return "yellow"
    if n in PURPLE_NUMBERS:
        return "purple"
    return "extra"


def ball_color_hex(n: int) -> str:
    return BALL_COLORS[ball_color_name(n)]


PRIZE_TIERS = {
    (6, False): "prize_1",
    (5, True): "prize_2",
    (5, False): "prize_3",
    (4, False): "prize_4",
    (3, False): "prize_5",
    (2, False): "prize_6",
}


def prize_tier(main_match: int, extra_matched: bool) -> str | None:
    return PRIZE_TIERS.get((main_match, extra_matched))
