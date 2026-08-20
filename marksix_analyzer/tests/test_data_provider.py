"""Tests for HKJC response parsing and CSV import validation (offline)."""
from __future__ import annotations

from UKLottoAnalyzer.data_provider import (
    HKJCProvider,
    import_csv,
    parse_row,
)

# A trimmed real-shape payload captured from the HKJC GraphQL endpoint.
SAMPLE_PAYLOAD = {
    "data": {
        "lotteryDraws": [
            {
                "id": "202673N",
                "year": "2026",
                "no": 73,
                "drawDate": "2026-07-07+08:00",
                "status": "Result",
                "lotteryPool": {"jackpot": "1897501"},
                "drawResult": {"drawnNo": [5, 34, 37, 43, 48, 49], "xDrawnNo": 27},
            },
            {
                "id": "202672",
                "year": "2026",
                "no": 72,
                "drawDate": "2026-07-05+08:00",
                "status": "Result",
                "lotteryPool": {"jackpot": "8,000,000"},
                "drawResult": {"drawnNo": [3, 14, 19, 20, 31, 38], "xDrawnNo": 44},
            },
            {   # future / undrawn draw -> must be skipped
                "id": "202674",
                "year": "2026",
                "no": 74,
                "drawDate": "2026-07-09+08:00",
                "status": "Sell",
                "lotteryPool": {"jackpot": ""},
                "drawResult": {"drawnNo": [], "xDrawnNo": None},
            },
        ]
    }
}


def test_parse_valid_draws():
    draws = HKJCProvider._parse(SAMPLE_PAYLOAD)
    assert len(draws) == 2  # undrawn entry skipped
    d = draws[0]
    assert d.draw_id == "26/073"
    assert d.draw_date == "2026-07-07"
    assert d.numbers == (5, 34, 37, 43, 48, 49)
    assert d.extra == 27
    assert d.jackpot == 1897501


def test_parse_jackpot_with_commas():
    draws = HKJCProvider._parse(SAMPLE_PAYLOAD)
    assert draws[1].jackpot == 8000000  # "8,000,000" parsed


def test_parse_empty_payload():
    assert HKJCProvider._parse({"data": {"lotteryDraws": None}}) == []
    assert HKJCProvider._parse({}) == []


def test_parse_draw_id_zero_padded():
    payload = {"data": {"lotteryDraws": [{
        "year": "2025", "no": 5, "drawDate": "2025-01-02+08:00",
        "lotteryPool": {"jackpot": None},
        "drawResult": {"drawnNo": [1, 2, 3, 4, 5, 6], "xDrawnNo": 7},
    }]}}
    draws = HKJCProvider._parse(payload)
    assert draws[0].draw_id == "25/005"
    assert draws[0].jackpot is None


# -- CSV validation --------------------------------------------------------
def test_parse_row_valid():
    row = {"draw_id": "24/001", "date": "2024-01-01",
           "n1": "1", "n2": "2", "n3": "3", "n4": "4", "n5": "5", "n6": "6",
           "extra": "7"}
    draw, err = parse_row(row, 2)
    assert err is None and draw.draw_id == "24/001"


def test_parse_row_out_of_range():
    row = {"draw_id": "24/001", "date": "2024-01-01",
           "n1": "50", "n2": "2", "n3": "3", "n4": "4", "n5": "5", "n6": "6",
           "extra": "7"}
    draw, err = parse_row(row, 5)
    assert draw is None and err.line == 5 and "1 至 49" in err.reason


def test_parse_row_duplicate_main():
    row = {"draw_id": "24/001", "date": "2024-01-01",
           "n1": "1", "n2": "1", "n3": "3", "n4": "4", "n5": "5", "n6": "6",
           "extra": "7"}
    draw, err = parse_row(row, 3)
    assert draw is None and "重複" in err.reason


def test_import_csv_roundtrip(tmp_path):
    p = tmp_path / "in.csv"
    p.write_text(
        "draw_id,date,n1,n2,n3,n4,n5,n6,extra\n"
        "24/001,2024-01-01,1,2,3,4,5,6,7\n"
        "24/002,2024-01-03,50,2,3,4,5,6,7\n"   # bad: 50 out of range
        "24/003,2024-01-05,10,20,30,40,45,49,1\n",
        encoding="utf-8",
    )
    draws, errors = import_csv(p)
    assert len(draws) == 2
    assert len(errors) == 1 and errors[0].line == 3
