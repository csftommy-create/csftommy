"""Smart Pick generator and rejection filters (pure, unit-testable).

Generates random 6-number combinations and rejects those failing enabled
filters. Uses ``secrets.SystemRandom`` for cryptographically-strong
randomness. This does NOT improve winning odds — it only filters out
statistically unusual / commonly-picked combinations.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from .analysis import max_consecutive_run
from .config import (
    MAIN_COUNT,
    MAX_NUMBER,
    MIN_NUMBER,
    prize_tier,
)
from .models import Draw

_rng = secrets.SystemRandom()


@dataclass
class FilterConfig:
    """User-toggleable rejection filters (defaults per spec section 5)."""

    odd_even: bool = True          # reject 6:0 or 0:6
    high_low: bool = True          # reject all-high or all-low
    sum_range: bool = True         # reject sum outside [sum_min, sum_max]
    sum_min: int = 90
    sum_max: int = 290
    consecutive: bool = True       # reject >= 3 consecutive
    same_tail: bool = True         # reject >= 3 sharing a tail digit
    birthday: bool = True          # reject all numbers <= 31
    arithmetic: bool = True        # reject arithmetic sequences
    exclude_last: bool = False     # reject any of last draw's numbers
    last_draw_numbers: list[int] = field(default_factory=list)


# --------------------------------------------------------------------------
# Individual rejection predicates: return True if the combo should be REJECTED
# --------------------------------------------------------------------------
def _reject_odd_even(nums: list[int]) -> bool:
    odd = sum(1 for n in nums if n % 2 == 1)
    return odd == 0 or odd == len(nums)


def _reject_high_low(nums: list[int], boundary: int = 29) -> bool:
    low = sum(1 <= n <= 29 for n in numbers)
    high = sum(30 <= n <= 59 for n in numbers)
    return low == 0 or low == len(nums)


def _reject_sum(nums: list[int], lo: int, hi: int) -> bool:
    return not (lo <= sum(nums) <= hi)


def _reject_consecutive(nums: list[int], max_allowed: int = 2) -> bool:
    return max_consecutive_run(nums) >= max_allowed + 1


def _reject_same_tail(nums: list[int], max_allowed: int = 2) -> bool:
    from collections import Counter

    tails = Counter(n % 10 for n in nums)
    return max(tails.values(), default=0) >= max_allowed + 1


def _reject_birthday(nums: list[int]) -> bool:
    return all(n <= 31 for n in nums)


def _reject_arithmetic(nums: list[int]) -> bool:
    s = sorted(nums)
    diffs = {s[i] - s[i - 1] for i in range(1, len(s))}
    return len(diffs) == 1  # constant difference => arithmetic sequence


def _reject_exclude_last(nums: list[int], last: list[int]) -> bool:
    return any(n in last for n in nums)


def is_rejected(nums: list[int], cfg: FilterConfig) -> tuple[bool, str | None]:
    """Return (rejected, reason_key). reason_key names the first failed rule."""
    if cfg.odd_even and _reject_odd_even(nums):
        return True, "odd_even"
    if cfg.high_low and _reject_high_low(nums):
        return True, "high_low"
    if cfg.sum_range and _reject_sum(nums, cfg.sum_min, cfg.sum_max):
        return True, "sum_range"
    if cfg.consecutive and _reject_consecutive(nums):
        return True, "consecutive"
    if cfg.same_tail and _reject_same_tail(nums):
        return True, "same_tail"
    if cfg.birthday and _reject_birthday(nums):
        return True, "birthday"
    if cfg.arithmetic and _reject_arithmetic(nums):
        return True, "arithmetic"
    if cfg.exclude_last and cfg.last_draw_numbers and _reject_exclude_last(
        nums, cfg.last_draw_numbers
    ):
        return True, "exclude_last"
    return False, None


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------
def _random_combo(rng=_rng) -> list[int]:
    return sorted(rng.sample(range(MIN_NUMBER, MAX_NUMBER + 1), MAIN_COUNT))


def generate_one(
    cfg: FilterConfig, max_attempts: int = 20000, rng=_rng
) -> list[int] | None:
    """Generate a single combo passing all enabled filters, or None."""
    for _ in range(max_attempts):
        combo = _random_combo(rng)
        rejected, _reason = is_rejected(combo, cfg)
        if not rejected:
            return combo
    return None


def generate(
    cfg: FilterConfig, count: int = 1, max_attempts: int = 20000, rng=_rng
) -> list[list[int]]:
    """Generate up to `count` distinct valid combos. May return fewer if the
    filters are too strict to satisfy within the attempt budget."""
    results: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    attempts = 0
    budget = max_attempts * max(count, 1)
    while len(results) < count and attempts < budget:
        combo = _random_combo(rng)
        attempts += 1
        key = tuple(combo)
        if key in seen:
            continue
        rejected, _ = is_rejected(combo, cfg)
        if not rejected:
            seen.add(key)
            results.append(combo)
    return results


# --------------------------------------------------------------------------
# 對獎 — prize checking against a historical draw
# --------------------------------------------------------------------------
def check_pick(pick_numbers: list[int], draw: Draw) -> dict:
    """Compare a 6-number pick against a draw, returning match info + tier."""
    pick_set = set(pick_numbers)
    main_matches = sorted(pick_set & set(draw.numbers))
    extra_matched = draw.extra in pick_set
    tier = prize_tier(len(main_matches), extra_matched)
    return {
        "main_matches": main_matches,
        "main_count": len(main_matches),
        "extra_matched": extra_matched,
        "tier": tier,  # prize key or None
        "draw_id": draw.draw_id,
        "draw_date": draw.draw_date,
    }
