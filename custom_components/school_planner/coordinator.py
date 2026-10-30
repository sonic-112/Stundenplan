"""Coordinator turning stored timetables into live state."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .schedule import (
    Lesson,
    compare,
    current_lesson,
    day_span,
    lessons_on,
    next_lesson,
)
from .store import PlannerStore

_LOGGER = logging.getLogger(__name__)


@dataclass
class ChildState:
    """Live state of one child."""

    child_id: str
    name: str
    school: dict[str, Any] | None
    free: bool
    lessons: list[Lesson]
    span: tuple[datetime, datetime] | None
    current: Lesson | None
    next: tuple[date, Lesson] | None


@dataclass
class PlannerData:
    """Everything the entities need."""

    children: dict[str, ChildState] = field(default_factory=dict)
    comparison: dict[str, Any] = field(default_factory=dict)


class SchoolPlannerCoordinator(DataUpdateCoordinator[PlannerData]):
    """Recomputes the state every minute and on every data change."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, store: PlannerStore
    ) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN)
        self.store = store

    async def _async_update_data(self) -> PlannerData:
        return self.compute()

    def compute(self) -> PlannerData:
        """Build the current state from the stored data."""
        now = dt_util.now().replace(tzinfo=None)
        today = now.date()
        data = PlannerData()
        entries = []
        for child_id, child in self.store.data["children"].items():
            entity = child.get("holiday_entity")
            free = bool(entity) and self.hass.states.is_state(entity, "on")
            timetable = child.get("timetable", {})
            lessons = [] if free else lessons_on(timetable, today)
            span = day_span(lessons, today)
            school = self.store.data["schools"].get(child.get("school_id") or "")
            data.children[child_id] = ChildState(
                child_id=child_id,
                name=child["name"],
                school=school,
                free=free,
                lessons=lessons,
                span=span,
                current=current_lesson(lessons, now),
                next=next_lesson(timetable, now, skip_today=free),
            )
            entries.append(
                {"id": child_id, "name": child["name"], "span": span, "school": school}
            )
        data.comparison = compare(entries)
        return data
