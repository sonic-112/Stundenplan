"""Tests for the pure scheduling logic."""

from datetime import date, datetime

from custom_components.school_planner.schedule import (
    compare,
    current_lesson,
    day_span,
    lessons_on,
    next_lesson,
)

MONDAY = date(2026, 11, 2)
TIMETABLE = {
    "0": [
        {"start": "09:00", "end": "09:45", "subject": "Maths"},
        {"start": "08:00", "end": "08:45", "subject": "German", "room": "A1"},
    ],
    "2": [{"start": "10:00", "end": "10:45", "subject": "Art"}],
}


def test_lessons_sorted():
    assert [l.subject for l in lessons_on(TIMETABLE, MONDAY)] == ["German", "Maths"]


def test_day_span_and_current():
    lessons = lessons_on(TIMETABLE, MONDAY)
    assert day_span(lessons, MONDAY) == (
        datetime(2026, 11, 2, 8, 0),
        datetime(2026, 11, 2, 9, 45),
    )
    assert current_lesson(lessons, datetime(2026, 11, 2, 8, 30)).subject == "German"
    assert current_lesson(lessons, datetime(2026, 11, 2, 8, 45)) is None
    assert day_span([], MONDAY) is None


def test_next_lesson_rolls_over_days():
    day, lesson = next_lesson(TIMETABLE, datetime(2026, 11, 2, 8, 30))
    assert (day, lesson.subject) == (MONDAY, "Maths")
    day, lesson = next_lesson(TIMETABLE, datetime(2026, 11, 2, 12, 0))
    assert (day, lesson.subject) == (date(2026, 11, 4), "Art")
    day, _ = next_lesson(TIMETABLE, datetime(2026, 11, 2, 7, 0), skip_today=True)
    assert day == date(2026, 11, 4)


def _entry(cid, start, end):
    span = (datetime(2026, 11, 2, *start), datetime(2026, 11, 2, *end)) if start else None
    return {"id": cid, "name": cid, "span": span, "school": None}


def test_compare():
    result = compare(
        [_entry("a", (8, 0), (12, 30)), _entry("b", (9, 0), (13, 15)), _entry("c", None, None)]
    )
    assert result["earliest_start"]["id"] == "a"
    assert result["latest_end"]["id"] == "b"
    assert [e["id"] for e in result["pickup_order"]] == ["a", "b"]
    assert result["gap_minutes"] == 45
    assert result["together_from"] == datetime(2026, 11, 2, 9, 0)
    assert result["together_until"] == datetime(2026, 11, 2, 12, 30)


def test_compare_without_overlap_and_empty():
    result = compare([_entry("a", (8, 0), (9, 0)), _entry("b", (10, 0), (11, 0))])
    assert result["together_from"] is None
    assert compare([_entry("a", None, None)])["pickup_order"] == []


def test_override_replaces_weekday_plan():
    overrides = {
        "2026-11-02": {"off": False, "lessons": [{"start": "10:00", "end": "10:45", "subject": "Sport"}]},
        "2026-11-04": {"off": True, "lessons": []},
    }
    assert [l.subject for l in lessons_on(TIMETABLE, MONDAY, overrides)] == ["Sport"]
    assert lessons_on(TIMETABLE, date(2026, 11, 4), overrides) == []
    # other weeks keep the regular plan
    assert len(lessons_on(TIMETABLE, date(2026, 11, 9), overrides)) == 2


def test_next_lesson_respects_overrides():
    overrides = {"2026-11-04": {"off": True, "lessons": []}}
    result = next_lesson(TIMETABLE, datetime(2026, 11, 2, 12, 0), overrides=overrides)
    assert result[0] == date(2026, 11, 9)  # Wednesday is off, so Monday of next week
