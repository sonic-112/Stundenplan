"""Voluptuous schemas shared by websocket API and services."""

from __future__ import annotations

from datetime import date, time
from typing import Any

import voluptuous as vol

from homeassistant.helpers import config_validation as cv

from .const import HOMEWARD, LESSON_STYLES, THEMES

TIME_RE = r"^([01]\d|2[0-3]):[0-5]\d$"
COLOR_RE = r"^#[0-9a-fA-F]{6}$"


def _lesson(value: dict[str, Any]) -> dict[str, Any]:
    """Validate that a lesson ends after it starts."""
    if time.fromisoformat(value["end"]) <= time.fromisoformat(value["start"]):
        raise vol.Invalid("end must be after start")
    return value


LESSON_SCHEMA = vol.All(
    vol.Schema(
        {
            vol.Required("start"): vol.Match(TIME_RE),
            vol.Required("end"): vol.Match(TIME_RE),
            vol.Required("subject"): vol.All(cv.string, vol.Length(min=1, max=60)),
            vol.Optional("room", default=""): vol.All(cv.string, vol.Length(max=40)),
            vol.Optional("teacher", default=""): vol.All(cv.string, vol.Length(max=60)),
            vol.Optional("color"): vol.Any(None, vol.Match(COLOR_RE)),
        }
    ),
    _lesson,
)


def iso_date(value: Any) -> str:
    """Accept an ISO date (YYYY-MM-DD) and return it normalised."""
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError as err:
        raise vol.Invalid("invalid date") from err


OVERRIDE_FIELDS = {
    vol.Required("date"): iso_date,
    vol.Optional("off", default=False): cv.boolean,
    vol.Optional("lessons", default=list): [LESSON_SCHEMA],
}

WEEKDAYS = [str(i) for i in range(7)]

TIMETABLE_SCHEMA = vol.Schema({vol.In(WEEKDAYS): [LESSON_SCHEMA]})

CHILD_FIELDS = {
    vol.Required("name"): vol.All(cv.string, vol.Length(min=1, max=40)),
    vol.Optional("color"): vol.Match(COLOR_RE),
    vol.Optional("school_id"): vol.Any(None, cv.string),
    vol.Optional("holiday_entity"): vol.Any(None, cv.entity_id),
    vol.Optional("homeward"): vol.In(HOMEWARD),
    vol.Optional("timetable"): TIMETABLE_SCHEMA,
}

SUBJECT_FIELDS = {
    vol.Required("subject"): vol.All(cv.string, vol.Length(min=1, max=30)),
    vol.Optional("name", default=""): vol.All(cv.string, vol.Length(max=60)),
    vol.Optional("color"): vol.Any(None, vol.Match(COLOR_RE)),
}

SCHOOL_FIELDS = {
    vol.Required("name"): vol.All(cv.string, vol.Length(min=1, max=80)),
    vol.Optional("address", default=""): vol.All(cv.string, vol.Length(max=200)),
    vol.Optional("zone"): vol.Any(None, cv.entity_id),
}

SETTINGS_FIELDS = {
    vol.Optional("theme"): vol.In(THEMES),
    vol.Optional("accent"): vol.Any(None, vol.Match(COLOR_RE)),
    vol.Optional("pickup_label"): vol.All(cv.string, vol.Length(min=1, max=30)),
    vol.Optional("sidebar"): cv.boolean,
    vol.Optional("lesson_style"): vol.In(LESSON_STYLES),
}
