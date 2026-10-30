"""Persistent storage for children, schools and timetables."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_COLORS,
    DEFAULT_HOMEWARD,
    DEFAULT_PICKUP_LABEL,
    DEFAULT_THEME,
    EVENT_UPDATED,
    OVERRIDE_KEEP_DAYS,
    STORAGE_KEY,
    STORAGE_VERSION,
)


def _empty() -> dict[str, Any]:
    return {
        "settings": {
            "theme": DEFAULT_THEME,
            "accent": None,
            "pickup_label": DEFAULT_PICKUP_LABEL,
        },
        "schools": {},
        "children": {},
    }


class PlannerStore:
    """Holds all user-maintained data."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.data: dict[str, Any] = _empty()
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        """Load data from disk."""
        stored = await self._store.async_load()
        if stored:
            self.data = {**_empty(), **stored}
            self.data["settings"] = {**_empty()["settings"], **self.data["settings"]}
            for child in self.data["children"].values():
                child.setdefault("homeward", DEFAULT_HOMEWARD)
                child.setdefault("overrides", {})
                self._prune(child)

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Call ``listener`` after every change."""
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    @callback
    def _changed(self) -> None:
        self._store.async_delay_save(lambda: self.data, 1)
        for listener in list(self._listeners):
            listener()
        self._hass.bus.async_fire(EVENT_UPDATED)

    # -- children ---------------------------------------------------------

    @callback
    def upsert_child(self, child_id: str | None, fields: dict[str, Any]) -> str:
        """Create or update a child and return its id."""
        children = self.data["children"]
        if child_id is None:
            child_id = uuid.uuid4().hex[:8]
            color = DEFAULT_COLORS[len(children) % len(DEFAULT_COLORS)]
            children[child_id] = {
                "name": "",
                "color": color,
                "school_id": None,
                "holiday_entity": None,
                "homeward": DEFAULT_HOMEWARD,
                "timetable": {},
                "overrides": {},
            }
        elif child_id not in children:
            raise KeyError(child_id)
        children[child_id].update(fields)
        self._changed()
        return child_id

    @callback
    def delete_child(self, child_id: str) -> None:
        """Remove a child."""
        if self.data["children"].pop(child_id, None) is None:
            raise KeyError(child_id)
        self._changed()

    @callback
    def set_day(self, child_id: str, weekday: str, lessons: list[dict[str, Any]]) -> None:
        """Replace the lessons of a single weekday."""
        child = self.data["children"][child_id]
        child["timetable"][weekday] = sorted(lessons, key=lambda l: l["start"])
        self._changed()

    @callback
    def set_override(
        self, child_id: str, day: str, *, off: bool, lessons: list[dict[str, Any]]
    ) -> None:
        """Replace one date with its own lessons or mark it as off.

        A date without lessons is the same as a date that is off.
        """
        child = self.data["children"][child_id]
        off = off or not lessons
        child["overrides"][day] = {
            "off": off,
            "lessons": [] if off else sorted(lessons, key=lambda l: l["start"]),
        }
        self._prune(child)
        self._changed()

    @callback
    def clear_override(self, child_id: str, day: str) -> None:
        """Return a date to the regular timetable."""
        if self.data["children"][child_id]["overrides"].pop(day, None) is not None:
            self._changed()

    @staticmethod
    def _prune(child: dict[str, Any]) -> None:
        """Drop overrides that lie far in the past."""
        limit = (dt_util.now().date() - timedelta(days=OVERRIDE_KEEP_DAYS)).isoformat()
        child["overrides"] = {d: o for d, o in child["overrides"].items() if d >= limit}

    # -- schools ----------------------------------------------------------

    @callback
    def upsert_school(self, school_id: str | None, fields: dict[str, Any]) -> str:
        """Create or update a school and return its id."""
        schools = self.data["schools"]
        if school_id is None:
            school_id = uuid.uuid4().hex[:8]
            schools[school_id] = {"name": "", "address": "", "zone": None}
        elif school_id not in schools:
            raise KeyError(school_id)
        schools[school_id].update(fields)
        self._changed()
        return school_id

    @callback
    def delete_school(self, school_id: str) -> None:
        """Remove a school and detach it from all children."""
        if self.data["schools"].pop(school_id, None) is None:
            raise KeyError(school_id)
        for child in self.data["children"].values():
            if child.get("school_id") == school_id:
                child["school_id"] = None
        self._changed()

    # -- settings ---------------------------------------------------------

    @callback
    def update_settings(self, fields: dict[str, Any]) -> None:
        """Update global settings."""
        self.data["settings"].update(fields)
        self._changed()
