"""Dev utility: regenerate seed_data.csv from HKJC's live endpoint.

This fetches the most recent draws HKJC exposes (currently ~50, back to
mid-2023) and writes them to the bundled seed_data.csv. Run it with network
access to refresh the bundled data before packaging:

    python -m UKLottoAnalyzer.tools.generate_seed

For deep historical data (back to 1993) HKJC's live API does not help —
import a community CSV dataset via 匯入 CSV instead.
"""
from __future__ import annotations

from pathlib import Path

from UKLottoAnalyzer.data_provider import HKJCProvider, export_csv

OUT = Path(__file__).resolve().parent.parent / "seed_data.csv"


def main() -> None:
    provider = HKJCProvider()
    provider.LAST_N = 4000  # ask for everything; server caps the result
    draws = sorted(provider.fetch_latest(), key=lambda d: (d.draw_date, d.draw_id))
    if not draws:
        print("No draws fetched (offline or endpoint changed). seed_data.csv "
              "left unchanged.")
        return
    n = export_csv(OUT, draws)
    print(f"Wrote {n} real HKJC draws "
          f"({draws[0].draw_id} … {draws[-1].draw_id}) to {OUT}")


if __name__ == "__main__":
    main()
