"""Data acquisition: DataProvider interface, HKJC fetcher, CSV import/export.

All fetching sits behind ``DataProvider`` so the source can be swapped
without touching the rest of the app. Network failures never raise past the
provider boundary — callers get an empty list / error object instead.
"""
from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from .models import Draw

CSV_HEADER = ["draw_id", "draw_date", "n1", "n2", "n3", "n4", "n5", "n6", "extra", "jackpot"]


def _to_int(value) -> int | None:
    """Best-effort int conversion; returns None for blanks / bad values."""
    if value in (None, "", "None"):
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
@dataclass
class RowError:
    line: int
    reason: str


def parse_row(
    row: dict | list, line_no: int
) -> tuple[Draw | None, RowError | None]:
    """Validate one CSV row. Returns (Draw, None) or (None, RowError)."""
    try:
        if isinstance(row, dict):
            draw_id = str(row.get("draw_id", "")).strip()
            date = str(row.get("date", "")).strip()
            nums = [int(str(row[f"n{i}"]).strip()) for i in range(1, 7)]
            extra = int(str(row.get("extra", "")).strip())
            jackpot = row.get("jackpot")
        else:
            draw_id = str(row[0]).strip()
            date = str(row[1]).strip()
            nums = [int(str(row[i]).strip()) for i in range(2, 8)]
            extra = int(str(row[8]).strip())
            jackpot = row[9] if len(row) > 9 else None
    except (KeyError, IndexError, ValueError, TypeError):
        return None, RowError(line_no, "欄位格式錯誤或缺少欄位")

    if not draw_id:
        return None, RowError(line_no, "缺少期數 draw_id")
    all_nums = nums + [extra]
    if any(not (1 <= n <= 49) for n in all_nums):
        return None, RowError(line_no, "號碼必須介乎 1 至 49")
    if len(set(nums)) != 6:
        return None, RowError(line_no, "六個主號碼不可重複")
    if extra in nums:
        return None, RowError(line_no, "特別號碼不可與主號碼重複")

    jk = None
    if jackpot not in (None, "", "None"):
        try:
            jk = int(float(jackpot))
        except (ValueError, TypeError):
            jk = None
    return Draw(draw_id=draw_id, draw_date=date,
                numbers=tuple(sorted(nums)), extra=extra, jackpot=jk), None


# --------------------------------------------------------------------------
# CSV import / export
# --------------------------------------------------------------------------
def import_csv(path: Path | str) -> tuple[list[Draw], list[RowError]]:
    """Parse a CSV file. Returns (valid_draws, errors_with_line_numbers)."""
    draws: list[Draw] = []
    errors: list[RowError] = []
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        has_header = reader.fieldnames and "n1" in [
            (c or "").strip().lower() for c in reader.fieldnames
        ]
        if has_header:
            # normalize header keys to lowercase
            for i, raw in enumerate(reader, start=2):  # line 2 = first data row
                row = {(k or "").strip().lower(): v for k, v in raw.items()}
                draw, err = parse_row(row, i)
                (draws if draw else errors).append(draw or err)
        else:
            f.seek(0)
            plain = csv.reader(f)
            for i, row in enumerate(plain, start=1):
                if not row or not str(row[0]).strip():
                    continue
                draw, err = parse_row(row, i)
                (draws if draw else errors).append(draw or err)
    return draws, errors


def export_csv(path: Path | str, draws: list[Draw]) -> int:
    path = Path(path)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER + ["jackpot"])
        for d in sorted(draws, key=lambda x: (x.draw_date, x.draw_id)):
            writer.writerow(
                [d.draw_id, d.draw_date, *sorted(d.numbers), d.extra,
                 d.jackpot if d.jackpot is not None else ""]
            )
    return len(draws)


def load_seed(path: Path | str) -> list[Draw]:
    """Load bundled seed data; returns [] if the file is missing/unreadable."""
    try:
        draws, _errors = import_csv(path)
        return draws
    except (OSError, UnicodeDecodeError):
        return []


# --------------------------------------------------------------------------
# DataProvider interface
# --------------------------------------------------------------------------
class DataProvider(ABC):
    """Abstract source of draw results."""

    @abstractmethod
    def fetch_latest(self, since_draw_id: str | None = None) -> list[Draw]:
        """Return draws newer than ``since_draw_id`` (may be empty)."""
        raise NotImplementedError


class HKJCProvider(DataProvider):
    """Fetches results from HKJC's public JSON endpoint.

    HKJC changes these endpoints periodically. This class isolates every
    network concern; on any failure it returns an empty list so the app
    keeps working offline. Update ``ENDPOINT`` / ``_parse`` when the API
    shape changes — nothing else in the app should need touching.
    """

    ENDPOINT = "https://info.cld.hkjc.com/graphql/base/"
    TIMEOUT = 15
    LAST_N = 30

    # The endpoint allowlists operations: it silently returns null unless the
    # query document matches a known operation *verbatim*. The fragment + query
    # below were extracted from HKJC's live bundle (bet.hkjc.com marksix
    # results). If HKJC changes the shape, re-capture from the site's JS and
    # update these two constants (and _parse) — nothing else needs touching.
    _FRAGMENT = (
        "fragment lotteryDrawsFragment on LotteryDraw {\n    id\n    year\n"
        "    no\n    openDate\n    closeDate\n    drawDate\n    status\n"
        "    snowballCode\n    snowballName_en\n    snowballName_ch\n"
        "    lotteryPool {\n      sell\n      status\n      totalInvestment\n"
        "      jackpot\n      unitBet\n      estimatedPrize\n"
        "      derivedFirstPrizeDiv\n      lotteryPrizes {\n        type\n"
        "        winningUnit\n        dividend\n      }\n    }\n"
        "    drawResult {\n      drawnNo\n      xDrawnNo\n    }\n  }"
    )
    QUERY = (
        "\n        " + _FRAGMENT + "\n        query marksixResult("
        "$lastNDraw: Int, $startDate: String, $endDate: String, "
        "$drawType: LotteryDrawType) {\n            lotteryDraws("
        "lastNDraw: $lastNDraw, startDate: $startDate, endDate: $endDate, "
        "drawType: $drawType) {\n              ...lotteryDrawsFragment\n"
        "            }\n        }\n    "
    )
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Origin": "https://bet.hkjc.com",
        "Referer": "https://bet.hkjc.com/en/marksix/results",
    }

    def fetch_latest(self, since_draw_id: str | None = None) -> list[Draw]:
        try:
            import requests  # local import: optional at runtime
        except ImportError:
            return []
        try:
            draws = self._fetch_via_graphql(requests)
        except Exception:
            return []
        # Return the whole batch; the DB upsert is idempotent (dedupes by id),
        # so we avoid fragile lexical id comparisons across year/format changes.
        return draws

    def _fetch_via_graphql(self, requests) -> list[Draw]:
        """Query the HKJC GraphQL endpoint for recent Mark Six draws.

        Defensive: any structural surprise raises and is swallowed by
        ``fetch_latest`` so the app stays usable offline.
        """
        body = {
            "operationName": "marksixResult",
            "query": self.QUERY,
            "variables": {"lastNDraw": self.LAST_N, "drawType": "All"},
        }
        resp = requests.post(self.ENDPOINT, json=body, timeout=self.TIMEOUT,
                             headers=self.HEADERS)
        resp.raise_for_status()
        return self._parse(resp.json())

    @staticmethod
    def _parse(payload: dict) -> list[Draw]:
        draws: list[Draw] = []
        items = (payload.get("data") or {}).get("lotteryDraws") or []
        for it in items:
            try:
                result = it.get("drawResult") or {}
                raw_nums = result.get("drawnNo") or []
                nums = [int(x) for x in raw_nums][:6]
                if len(nums) != 6:
                    continue  # skip future / undrawn entries
                extra = int(result["xDrawnNo"])
                # Public draw number, e.g. year 2026 + no 73 -> "26/073".
                draw_id = f"{int(it['year']) % 100:02d}/{int(it['no']):03d}"
                pool = it.get("lotteryPool") or {}
                jackpot = _to_int(pool.get("jackpot"))
                draws.append(
                    Draw(
                        draw_id=draw_id,
                        draw_date=str(it["drawDate"])[:10],
                        numbers=tuple(sorted(nums)),
                        extra=extra,
                        jackpot=jackpot,
                    )
                )
            except (KeyError, ValueError, TypeError):
                continue
        return draws


class NullProvider(DataProvider):
    """Offline no-op provider (used when networking is unavailable)."""

    def fetch_latest(self, since_draw_id: str | None = None) -> list[Draw]:
        return []
