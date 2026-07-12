"""Lightweight data models shared across layers (no Qt / no DB deps)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Draw:
    """A single Mark Six draw result. Main numbers stored sorted ascending."""

    draw_id: str
    draw_date: str  # ISO "YYYY-MM-DD"
    numbers: tuple[int, int, int, int, int, int]
    extra: int
    jackpot: int | None = None

    def __post_init__(self) -> None:
        # Enforce sorted ascending, immutable via object.__setattr__.
        if list(self.numbers) != sorted(self.numbers):
            object.__setattr__(self, "numbers", tuple(sorted(self.numbers)))

    @property
    def all_numbers(self) -> tuple[int, ...]:
        """Main six plus the extra (特別號碼)."""
        return tuple(sorted(self.numbers)) + (self.extra,)


@dataclass
class Pick:
    """A user or generated selection of six numbers."""

    numbers: list[int] = field(default_factory=list)
    method: str = "manual"  # "smart" | "random" | "manual"
    note: str = ""
    id: int | None = None
    created_at: str | None = None
