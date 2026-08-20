"""Unit tests for pure analysis functions."""
from __future__ import annotations

import pytest

from UKLottoAnalyzer import analysis
from UKLottoAnalyzer.models import Draw


def make(draw_id, date, nums, extra):
    return Draw(draw_id=draw_id, draw_date=date, numbers=tuple(nums), extra=extra)


@pytest.fixture
def draws():
    return [
        make("24/001", "2024-01-01", [1, 2, 3, 10, 20, 30], 5),
        make("24/002", "2024-01-03", [1, 2, 4, 11, 21, 31], 6),
        make("24/003", "2024-01-05", [1, 5, 9, 13, 25, 40], 7),
    ]


def test_draw_sorts_numbers():
    d = make("x", "2024-01-01", [30, 2, 10, 1, 20, 3], 5)
    assert d.numbers == (1, 2, 3, 10, 20, 30)


def test_frequency(draws):
    freq = analysis.frequency(draws)
    assert freq[1] == 3  # appears in all three
    assert freq[2] == 2
    assert freq[49] == 0
    assert sum(freq.values()) == 6 * len(draws)


def test_frequency_include_extra(draws):
    freq = analysis.frequency(draws, include_extra=True)
    assert freq[5] == 2  # once as main, once as extra
    assert sum(freq.values()) == 7 * len(draws)


def test_hot_cold(draws):
    hot, cold = analysis.hot_cold(draws, top=3)
    assert 1 in hot  # most frequent
    assert len(hot) == 3 and len(cold) == 3


def test_filter_last_n(draws):
    out = analysis.filter_draws(draws, last_n=2)
    assert [d.draw_id for d in out] == ["24/002", "24/003"]


def test_filter_date_range(draws):
    out = analysis.filter_draws(draws, date_from="2024-01-03", date_to="2024-01-05")
    assert [d.draw_id for d in out] == ["24/002", "24/003"]


def test_gaps_current(draws):
    g = analysis.gaps(draws)
    # number 1 appears in the latest draw -> current gap 0
    assert g[1]["current_gap"] == 0
    # number 30 last appeared in first draw (index 0); total 3 -> gap 2
    assert g[30]["current_gap"] == 2
    # a never-drawn number
    assert g[49]["current_gap"] == len(draws)


def test_odd_even_ratio():
    assert analysis.odd_even_ratio([1, 3, 5, 2, 4, 6]) == (3, 3)
    assert analysis.odd_even_ratio([1, 3, 5, 7, 9, 11]) == (6, 0)


def test_high_low_split():
    assert analysis.high_low_split([1, 2, 3, 25, 26, 49]) == (3, 3)


def test_sum_stats(draws):
    st = analysis.sum_stats(draws)
    assert st["min"] <= st["mean"] <= st["max"]
    assert len(st["sums"]) == len(draws)


def test_max_consecutive_run():
    assert analysis.max_consecutive_run([1, 2, 3, 10, 20, 30]) == 3
    assert analysis.max_consecutive_run([1, 5, 9, 13, 25, 40]) == 1
    assert analysis.max_consecutive_run([]) == 0


def test_consecutive_stats(draws):
    cs = analysis.consecutive_stats(draws)
    # first two draws contain consecutive numbers, third does not
    assert cs["count"] == 2
    assert cs["total"] == 3


def test_tail_frequency(draws):
    tails = analysis.tail_frequency(draws)
    assert sum(tails.values()) == 6 * len(draws)


def test_same_tail_stats():
    d = [make("x", "2024-01-01", [1, 11, 21, 5, 15, 25], 9)]
    # tails: 1,1,1,5,5,5 -> max count 3 >= 2
    assert analysis.same_tail_stats(d)["count"] == 1


def test_top_pairs(draws):
    pairs = analysis.top_pairs(draws, top=5)
    assert pairs[0]["pair"] == (1, 2)  # appears twice
    assert pairs[0]["count"] == 2


def test_trend_points(draws):
    pts = analysis.trend_points(draws, last_n=2)
    # 2 draws * (6 main + 1 extra) = 14 points
    assert len(pts) == 14
    assert any(p["extra"] for p in pts)
