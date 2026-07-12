"""Pure analysis functions (no Qt, no DB).

Every function takes a list of ``Draw`` objects and plain parameters, and
returns plain data structures so they are trivially unit-testable.
"""
from __future__ import annotations

import statistics
from collections import Counter
from itertools import combinations

from .config import MAX_NUMBER, MIN_NUMBER
from .models import Draw

ALL_NUMBERS = range(MIN_NUMBER, MAX_NUMBER + 1)


# --------------------------------------------------------------------------
# Range / filter helpers
# --------------------------------------------------------------------------
def filter_draws(
    draws: list[Draw],
    last_n: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> list[Draw]:
    """Filter a chronologically-sorted (oldest first) draw list.

    ``last_n`` keeps the most recent N draws. Date bounds are inclusive ISO
    strings. Filters combine (date bounds applied first, then last_n).
    """
    result = draws
    if date_from is not None:
        result = [d for d in result if d.draw_date >= date_from]
    if date_to is not None:
        result = [d for d in result if d.draw_date <= date_to]
    if last_n is not None and last_n > 0:
        result = result[-last_n:]
    return result


def _numbers_of(draw: Draw, include_extra: bool) -> tuple[int, ...]:
    return draw.all_numbers if include_extra else draw.numbers


# --------------------------------------------------------------------------
# 4.1 Frequency analysis (號碼頻率)
# --------------------------------------------------------------------------
def frequency(draws: list[Draw], include_extra: bool = False) -> dict[int, int]:
    """Count appearances per number 1-49. Always returns every number."""
    counts = Counter()
    for d in draws:
        counts.update(_numbers_of(d, include_extra))
    return {n: counts.get(n, 0) for n in ALL_NUMBERS}


def frequency_table(
    draws: list[Draw], include_extra: bool = False
) -> list[dict]:
    """Sorted-by-count-desc rows with percentage of draws."""
    freq = frequency(draws, include_extra)
    total = len(draws) or 1
    rows = [
        {"number": n, "count": c, "pct": 100.0 * c / total}
        for n, c in freq.items()
    ]
    rows.sort(key=lambda r: (-r["count"], r["number"]))
    return rows


def hot_cold(
    draws: list[Draw], top: int = 10, include_extra: bool = False
) -> tuple[list[int], list[int]]:
    """Return (hot_numbers, cold_numbers) as the top/bottom `top` by count."""
    rows = frequency_table(draws, include_extra)
    hot = [r["number"] for r in rows[:top]]
    cold = [r["number"] for r in rows[-top:]]
    return hot, cold


# --------------------------------------------------------------------------
# 4.2 Gap analysis (遺漏分析)
# --------------------------------------------------------------------------
def gaps(draws: list[Draw]) -> dict[int, dict]:
    """For each number: current gap, max gap, average gap, last-seen date.

    Draws must be oldest-first. ``current_gap`` = number of draws since the
    last appearance (0 if it appeared in the most recent draw). If a number
    never appeared, current_gap == len(draws), max_gap == len(draws),
    avg_gap == len(draws).
    """
    total = len(draws)
    result: dict[int, dict] = {}
    for n in ALL_NUMBERS:
        appearances = [i for i, d in enumerate(draws) if n in d.numbers]
        if not appearances:
            result[n] = {
                "current_gap": total,
                "max_gap": total,
                "avg_gap": float(total),
                "last_date": None,
                "count": 0,
            }
            continue
        # gaps between consecutive appearances
        intervals = [
            appearances[i] - appearances[i - 1]
            for i in range(1, len(appearances))
        ]
        current_gap = total - 1 - appearances[-1]
        # include the leading gap (before first appearance) and current gap
        gap_samples = intervals if intervals else []
        max_gap = max(gap_samples + [appearances[0] + 1, current_gap + 1]) - 0
        max_gap = max(max_gap, current_gap)
        avg_gap = (
            statistics.mean(intervals) if intervals else float(total)
        )
        result[n] = {
            "current_gap": current_gap,
            "max_gap": max(max_gap, current_gap),
            "avg_gap": float(avg_gap),
            "last_date": draws[appearances[-1]].draw_date,
            "count": len(appearances),
        }
    return result


def gap_table(draws: list[Draw]) -> list[dict]:
    g = gaps(draws)
    rows = []
    for n in ALL_NUMBERS:
        info = g[n]
        rows.append(
            {
                "number": n,
                "current_gap": info["current_gap"],
                "max_gap": info["max_gap"],
                "avg_gap": info["avg_gap"],
                "last_date": info["last_date"],
                "over_average": info["current_gap"] > info["avg_gap"],
            }
        )
    rows.sort(key=lambda r: -r["current_gap"])
    return rows


# --------------------------------------------------------------------------
# 4.3 Distribution analysis (分佈分析)
# --------------------------------------------------------------------------
def odd_even_ratio(numbers) -> tuple[int, int]:
    odd = sum(1 for n in numbers if n % 2 == 1)
    return odd, len(numbers) - odd


def high_low_split(numbers, boundary: int = 24) -> tuple[int, int]:
    low = sum(1 for n in numbers if n <= boundary)
    return len(numbers) - low, low  # (high, low)


def odd_even_distribution(draws: list[Draw]) -> dict[str, int]:
    """Histogram of odd:even ratios across draws, e.g. {'3:3': 120, ...}."""
    dist = Counter()
    for d in draws:
        odd, even = odd_even_ratio(d.numbers)
        dist[f"{odd}:{even}"] += 1
    return dict(sorted(dist.items(), reverse=True))


def high_low_distribution(draws: list[Draw]) -> dict[str, int]:
    dist = Counter()
    for d in draws:
        high, low = high_low_split(d.numbers)
        dist[f"{high}:{low}"] += 1
    return dict(sorted(dist.items(), reverse=True))


def sum_stats(draws: list[Draw]) -> dict:
    sums = [sum(d.numbers) for d in draws]
    if not sums:
        return {"sums": [], "mean": 0.0, "median": 0.0, "std": 0.0,
                "min": 0, "max": 0, "histogram": {}}
    hist = Counter(sums)
    return {
        "sums": sums,
        "mean": statistics.mean(sums),
        "median": statistics.median(sums),
        "std": statistics.pstdev(sums) if len(sums) > 1 else 0.0,
        "min": min(sums),
        "max": max(sums),
        "histogram": dict(sorted(hist.items())),
    }


def max_consecutive_run(numbers) -> int:
    """Length of the longest consecutive run in a set of numbers."""
    nums = sorted(set(numbers))
    if not nums:
        return 0
    best = run = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i - 1] + 1:
            run += 1
            best = max(best, run)
        else:
            run = 1
    return best


def consecutive_stats(draws: list[Draw]) -> dict:
    """How often draws contain >=2 consecutive numbers."""
    total = len(draws) or 1
    with_consec = sum(1 for d in draws if max_consecutive_run(d.numbers) >= 2)
    return {
        "count": with_consec,
        "total": len(draws),
        "pct": 100.0 * with_consec / total,
    }


# --------------------------------------------------------------------------
# 4.4 Tail digit analysis (尾數分析)
# --------------------------------------------------------------------------
def tail_frequency(draws: list[Draw], include_extra: bool = False) -> dict[int, int]:
    counts = Counter()
    for d in draws:
        for n in _numbers_of(d, include_extra):
            counts[n % 10] += 1
    return {t: counts.get(t, 0) for t in range(10)}


def same_tail_stats(draws: list[Draw], threshold: int = 2) -> dict:
    """How often a draw contains >= threshold numbers sharing a tail digit."""
    total = len(draws) or 1
    hits = 0
    for d in draws:
        tail_counts = Counter(n % 10 for n in d.numbers)
        if max(tail_counts.values(), default=0) >= threshold:
            hits += 1
    return {"count": hits, "total": len(draws), "pct": 100.0 * hits / total}


# --------------------------------------------------------------------------
# 4.5 Pair / combination frequency (組合分析)
# --------------------------------------------------------------------------
def top_pairs(draws: list[Draw], top: int = 20) -> list[dict]:
    counts = Counter()
    for d in draws:
        for a, b in combinations(sorted(d.numbers), 2):
            counts[(a, b)] += 1
    rows = [
        {"pair": pair, "count": c}
        for pair, c in counts.most_common(top)
    ]
    return rows


# --------------------------------------------------------------------------
# 4.6 Trend view data (近期走勢)
# --------------------------------------------------------------------------
def trend_points(draws: list[Draw], last_n: int = 50) -> list[dict]:
    """Return scatter points: {'x': draw_index, 'y': number, 'extra': bool}."""
    recent = draws[-last_n:] if last_n else draws
    points = []
    for x, d in enumerate(recent):
        for n in d.numbers:
            points.append({"x": x, "y": n, "extra": False,
                           "draw_id": d.draw_id})
        points.append({"x": x, "y": d.extra, "extra": True,
                       "draw_id": d.draw_id})
    return points
