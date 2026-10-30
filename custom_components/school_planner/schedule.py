"""Pure scheduling logic, independent of Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any


@dataclass(frozen=True)
class Lesson:
    """A single lesson on a weekday."""

    start: time
    end: time
    subject: str
    room: str = ""
    teacher: str = ""
    color: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lesson:
        """Build a lesson from its stored representation."""
        return cls(
            start=time.fromisoformat(data["start"]),
            end=time.fromisoformat(data["end"]),
            subject=data["subject"],
            room=data.get("room", ""),
            teacher=data.get("teacher", ""),
            color=data.get("color"),
        )


def lessons_on(
    timetable: dict[str, list[dict[str, Any]]],
    day: date,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> list[Lesson]:
    """Return the lessons of a day sorted by start time.

    An override for that exact date replaces the regular weekday plan.
    """
    override = (overrides or {}).get(day.isoformat())
    if override is not None:
        raw = [] if override.get("off") else override.get("lessons", [])
    else:
        raw = timetable.get(str(day.weekday()), [])
    return sorted((Lesson.from_dict(item) for item in raw), key=lambda l: l.start)


def day_span(lessons: list[Lesson], day: date) -> tuple[datetime, datetime] | None:
    """Return first start and last end of a day, or None without lessons."""
    if not lessons:
        return None
    return (
        datetime.combine(day, lessons[0].start),
        datetime.combine(day, max(l.end for l in lessons)),
    )


def current_lesson(lessons: list[Lesson], now: datetime) -> Lesson | None:
    """Return the lesson running at ``now``."""
    t = now.time()
    for lesson in lessons:
        if lesson.start <= t < lesson.end:
            return lesson
    return None


def next_lesson(
    timetable: dict[str, list[dict[str, Any]]],
    now: datetime,
    *,
    skip_today: bool = False,
    horizon: int = 14,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> tuple[date, Lesson] | None:
    """Return the next lesson that starts after ``now``."""
    for offset in range(horizon):
        if offset == 0 and skip_today:
            continue
        day = now.date() + timedelta(days=offset)
        for lesson in lessons_on(timetable, day, overrides):
            if offset > 0 or lesson.start > now.time():
                return day, lesson
    return None


def compare(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare the school days of several children.

    Each entry needs ``id``, ``name`` and ``span`` (``(start, end)`` or None).
    """
    active = [e for e in entries if e["span"]]
    if not active:
        return {
            "earliest_start": None,
            "latest_end": None,
            "first_done": None,
            "last_done": None,
            "pickup_order": [],
            "gap_minutes": None,
            "together_from": None,
            "together_until": None,
        }

    def view(entry: dict[str, Any]) -> dict[str, Any]:
        start, end = entry["span"]
        return {
            "id": entry["id"],
            "name": entry["name"],
            "start": start,
            "end": end,
            "school": entry.get("school"),
        }

    by_end = sorted(active, key=lambda e: e["span"][1])
    earliest = min(active, key=lambda e: e["span"][0])
    latest = max(active, key=lambda e: e["span"][1])
    from_ = max(e["span"][0] for e in active)
    until = min(e["span"][1] for e in active)
    return {
        "earliest_start": view(earliest),
        "latest_end": view(latest),
        "first_done": view(by_end[0]),
        "last_done": view(by_end[-1]),
        "pickup_order": [view(e) for e in by_end],
        "gap_minutes": int((by_end[-1]["span"][1] - by_end[0]["span"][1]).total_seconds() // 60),
        "together_from": from_ if from_ < until else None,
        "together_until": until if from_ < until else None,
    }
