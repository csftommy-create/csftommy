"""Unit tests for smart pick filters, generation, and prize checking."""
from __future__ import annotations

import random

import pytest

from marksix_analyzer import smart_pick
from marksix_analyzer.models import Draw
from marksix_analyzer.smart_pick import FilterConfig, is_rejected


def cfg(**kwargs) -> FilterConfig:
    # Start with everything OFF, enable only what a test needs.
    base = FilterConfig(
        odd_even=False, high_low=False, sum_range=False, consecutive=False,
        same_tail=False, birthday=False, arithmetic=False, exclude_last=False,
    )
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


# -- individual rejection rules --------------------------------------------
def test_reject_odd_even_all_odd():
    r, reason = is_rejected([1, 3, 5, 7, 9, 11], cfg(odd_even=True))
    assert r and reason == "odd_even"


def test_reject_odd_even_all_even():
    r, _ = is_rejected([2, 4, 6, 8, 10, 12], cfg(odd_even=True))
    assert r


def test_accept_odd_even_mixed():
    r, _ = is_rejected([1, 2, 3, 4, 5, 6], cfg(odd_even=True))
    assert not r


def test_reject_high_low_all_high():
    r, reason = is_rejected([25, 30, 35, 40, 45, 49], cfg(high_low=True))
    assert r and reason == "high_low"


def test_reject_high_low_all_low():
    r, _ = is_rejected([1, 5, 10, 15, 20, 24], cfg(high_low=True))
    assert r


def test_reject_sum_below():
    r, reason = is_rejected([1, 2, 3, 4, 5, 6], cfg(sum_range=True, sum_min=100, sum_max=200))
    assert r and reason == "sum_range"


def test_reject_sum_above():
    r, _ = is_rejected([44, 45, 46, 47, 48, 49], cfg(sum_range=True, sum_min=100, sum_max=200))
    assert r


def test_accept_sum_within():
    r, _ = is_rejected([10, 20, 30, 40, 45, 5], cfg(sum_range=True, sum_min=100, sum_max=200))
    assert not r  # sum = 150


def test_reject_three_consecutive():
    r, reason = is_rejected([1, 2, 3, 20, 30, 40], cfg(consecutive=True))
    assert r and reason == "consecutive"


def test_accept_two_consecutive():
    r, _ = is_rejected([1, 2, 20, 30, 40, 45], cfg(consecutive=True))
    assert not r  # only 2 consecutive allowed


def test_reject_three_same_tail():
    r, reason = is_rejected([1, 11, 21, 5, 15, 40], cfg(same_tail=True))
    assert r and reason == "same_tail"


def test_accept_two_same_tail():
    r, _ = is_rejected([1, 11, 5, 15, 30, 42], cfg(same_tail=True))
    assert not r


def test_reject_birthday():
    r, reason = is_rejected([1, 5, 12, 18, 25, 31], cfg(birthday=True))
    assert r and reason == "birthday"


def test_accept_non_birthday():
    r, _ = is_rejected([1, 5, 12, 18, 25, 40], cfg(birthday=True))
    assert not r  # 40 > 31


def test_reject_arithmetic():
    r, reason = is_rejected([5, 10, 15, 20, 25, 30], cfg(arithmetic=True))
    assert r and reason == "arithmetic"


def test_reject_arithmetic_step_one():
    r, _ = is_rejected([1, 2, 3, 4, 5, 6], cfg(arithmetic=True))
    assert r


def test_accept_non_arithmetic():
    r, _ = is_rejected([1, 2, 4, 8, 16, 32], cfg(arithmetic=True))
    assert not r


def test_reject_exclude_last():
    c = cfg(exclude_last=True)
    c.last_draw_numbers = [7, 14, 21, 28, 35, 42]
    r, reason = is_rejected([7, 1, 3, 5, 9, 11], c)
    assert r and reason == "exclude_last"


# -- generation ------------------------------------------------------------
def test_generate_respects_all_filters():
    c = FilterConfig()  # all defaults ON
    rng = random.Random(42)
    combos = smart_pick.generate(c, count=10, rng=rng)
    assert len(combos) == 10
    for combo in combos:
        rejected, reason = is_rejected(combo, c)
        assert not rejected, f"{combo} failed {reason}"
        assert len(set(combo)) == 6
        assert combo == sorted(combo)


def test_generate_distinct():
    combos = smart_pick.generate(FilterConfig(), count=5, rng=random.Random(1))
    keys = {tuple(c) for c in combos}
    assert len(keys) == len(combos)


# -- prize checking --------------------------------------------------------
def draw():
    return Draw(draw_id="24/100", draw_date="2024-06-01",
                numbers=(3, 11, 22, 30, 41, 49), extra=7)


@pytest.mark.parametrize("pick, expect_tier", [
    ([3, 11, 22, 30, 41, 49], "prize_1"),          # 6 main
    ([3, 11, 22, 30, 41, 7], "prize_2"),           # 5 + extra
    ([3, 11, 22, 30, 41, 8], "prize_3"),           # 5 main
    ([3, 11, 22, 30, 7, 8], "prize_4"),            # 4 + extra
    ([3, 11, 22, 30, 8, 9], "prize_5"),            # 4 main
    ([3, 11, 22, 7, 8, 9], "prize_6"),             # 3 + extra
    ([3, 11, 22, 8, 9, 10], "prize_7"),            # 3 main
    ([1, 2, 4, 5, 6, 8], None),                    # nothing
])
def test_prize_tiers(pick, expect_tier):
    res = smart_pick.check_pick(pick, draw())
    assert res["tier"] == expect_tier


def test_check_pick_match_details():
    res = smart_pick.check_pick([3, 11, 22, 30, 41, 7], draw())
    assert res["main_count"] == 5
    assert res["extra_matched"] is True
    assert res["main_matches"] == [3, 11, 22, 30, 41]
