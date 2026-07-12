# MarkSix Analyzer（六合彩數據分析器）

A desktop GUI application for analyzing historical Hong Kong Mark Six (六合彩)
draw results and generating statistically-filtered number combinations.

> **重要聲明 / Disclaimer**
> This is a **statistics and analysis** tool, **not** a prediction tool.
> Every draw is an independent random event; no method can predict future
> results. The "Smart Pick" feature only filters out statistically unusual or
> commonly-picked combinations to reduce jackpot-splitting risk — it does
> **not** improve winning odds.

UI language: Traditional Chinese (繁體中文).

---

## Features

- **總覽 (Dashboard)** — latest draw as colored balls, quick stats, mini chart.
- **號碼頻率 (Frequency)** — bar chart + sortable table, hot/cold highlighting.
- **遺漏分析 (Gaps)** — current / max / average gap per number, heat coloring.
- **分佈統計 (Distribution)** — sum histogram, odd/even, high/low, consecutive,
  tail-digit stats.
- **走勢圖 (Trend)** — classic scatter trend chart for the last 30–100 draws.
- **智能選號 (Smart Pick)** — 8 toggleable rejection filters, `secrets`-based
  randomness, colored ball display, save / copy.
- **我的號碼 (Saved Picks)** — save picks and 對獎 against any historical draw,
  identifying all 7 official prize tiers.
- **資料管理 (Data)** — paginated history, CSV import/export, manual entry,
  background refresh from HKJC, DB stats.

All network and heavy work runs off the UI thread; the app is **fully usable
offline** with the bundled seed data.

**Bilingual UI** — a 🌐 toggle in the header switches the whole interface
between Traditional Chinese (繁體中文) and English at runtime; the choice is
remembered across restarts (`QSettings`). All strings live in
[`strings.py`](marksix_analyzer/strings.py) as `zh`/`en` locale dicts.

---

## Requirements

- Python 3.11+
- See [`marksix_analyzer/requirements.txt`](marksix_analyzer/requirements.txt)

```bash
pip install -r marksix_analyzer/requirements.txt
```

## Run (from source)

```bash
python run.py
# or
python -m marksix_analyzer
```

On first launch the bundled `seed_data.csv` is imported into a SQLite database
in your user data directory:

- Windows: `%APPDATA%\MarkSixAnalyzer\marksix.db`
- macOS: `~/Library/Application Support/MarkSixAnalyzer/marksix.db`

> The bundled `seed_data.csv` contains **real HKJC history from 2002-07-04**
> (the date Mark Six switched to the 6-from-49 format) **to 2025-12-28** —
> 3,277 draws. On launch the app auto-fetches the latest draws from HKJC's live
> API to fill anything newer. CSV columns:
> `draw_id, date, n1..n6, extra` (optional `jackpot`).
>
> The seed is versioned (`config.SEED_VERSION`): when the bundled file is
> updated, existing databases re-import it automatically on next launch
> (idempotent upsert — saved picks are never touched). Deep pre-2002 history is
> deliberately excluded because the number range differed (1–47 / 1–36), which
> would skew frequency and gap statistics.

## Tests

```bash
pytest marksix_analyzer/tests -q
```

The pure logic (`analysis.py`, `smart_pick.py`) is fully unit-tested — including
proof that every Smart Pick filter rejects correctly and that all 7 prize tiers
are identified.

---

## Data source

Draw data is fetched behind a `DataProvider` interface (`data_provider.py`) so
the source can be swapped without touching the rest of the app.

`HKJCProvider` uses HKJC's live GraphQL endpoint
`https://info.cld.hkjc.com/graphql/base/`, calling the `marksixResult`
operation (`lotteryDraws(drawType: "All", lastNDraw: …)`). Verified against the
live site. Two things to know if it ever breaks:

- **The endpoint allowlists operations** — it silently returns `null` unless the
  query document matches a known operation *verbatim*, so `HKJCProvider.QUERY`
  and `_FRAGMENT` must stay byte-for-byte. Re-capture them from the site's JS
  bundle (`bet.hkjc.com/static/js/main.*.js`, search `lotteryDrawsFragment`) if
  HKJC changes the shape, then adjust `_parse`. Nothing else needs touching.
- HKJC's API only exposes **recent** draws (~50). Any network failure degrades
  gracefully to offline mode.

The bundled historical `seed_data.csv` (2002-07-04 → 2025-12-28) was compiled
from the public [icelam/mark-six-data-visualization](https://github.com/icelam/mark-six-data-visualization)
dataset, filtered to the 6-from-49 era and re-validated (6 distinct numbers
1–49, extra distinct, no duplicate draw ids).

---

## Packaging

Install PyInstaller (`pip install pyinstaller`), then:

```bash
pyinstaller MarkSixAnalyzer.spec
```

### Windows
Output: `dist/MarkSixAnalyzer.exe` (single-file, windowed). Provide `app.ico`
in the project root, or remove the `icon=` line from the spec.

### macOS
Output: `dist/MarkSixAnalyzer.app`. Build on Apple Silicon (arm64); Intel users
may need a separate build or Rosetta. The app is unsigned — right-click → Open
to bypass Gatekeeper, or run `xattr -cr MarkSixAnalyzer.app`.

---

## Project layout

```
run.py                     # launcher / PyInstaller entry
MarkSixAnalyzer.spec       # PyInstaller build spec
marksix_analyzer/
├── main.py                # QApplication setup
├── config.py              # paths, ball colors, prize tiers, version
├── strings.py             # all UI strings (Traditional Chinese)
├── models.py              # Draw / Pick dataclasses
├── db.py                  # SQLite layer (all SQL)
├── data_provider.py       # DataProvider + HKJC fetcher + CSV import/export
├── analysis.py            # pure analysis functions (unit-testable)
├── smart_pick.py          # generator + rejection filters + prize check
├── workers.py             # QThread fetch workers
├── seed_data.csv          # bundled (demo) historical results
├── tools/generate_seed.py # regenerates the demo seed
├── ui/                    # PySide6 widgets and the 8 tabs
└── tests/                 # pytest suite
```
