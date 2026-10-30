"""Sensors for School Planner."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import SchoolPlannerConfigEntry
from .const import DOMAIN
from .coordinator import ChildState, PlannerData, SchoolPlannerCoordinator

PARALLEL_UPDATES = 0


def _aware(value: datetime | None) -> datetime | None:
    return value.replace(tzinfo=dt_util.get_default_time_zone()) if value else None


def _lesson_attrs(lesson) -> dict[str, Any]:
    if lesson is None:
        return {}
    return {
        "start": lesson.start.strftime("%H:%M"),
        "end": lesson.end.strftime("%H:%M"),
        "room": lesson.room,
        "teacher": lesson.teacher,
    }


@dataclass(frozen=True, kw_only=True)
class ChildSensorDescription(SensorEntityDescription):
    """Description of a per-child sensor."""

    value_fn: Callable[[ChildState], Any]
    attrs_fn: Callable[[ChildState], dict[str, Any]] = lambda _: {}


@dataclass(frozen=True, kw_only=True)
class HubSensorDescription(SensorEntityDescription):
    """Description of a sensor comparing all children."""

    value_fn: Callable[[dict[str, Any]], Any]


def _school_attrs(state: ChildState) -> dict[str, Any]:
    school = state.school or {}
    return {
        "child": state.name,
        "school": school.get("name"),
        "address": school.get("address"),
        "zone": school.get("zone"),
    }


CHILD_SENSORS: tuple[ChildSensorDescription, ...] = (
    ChildSensorDescription(
        key="current_lesson",
        translation_key="current_lesson",
        value_fn=lambda s: s.current.subject if s.current else None,
        attrs_fn=lambda s: _lesson_attrs(s.current) | {"free_day": s.free},
    ),
    ChildSensorDescription(
        key="next_lesson",
        translation_key="next_lesson",
        value_fn=lambda s: s.next[1].subject if s.next else None,
        attrs_fn=lambda s: (
            _lesson_attrs(s.next[1]) | {"date": s.next[0].isoformat()} if s.next else {}
        ),
    ),
    ChildSensorDescription(
        key="school_start",
        translation_key="school_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: _aware(s.span[0]) if s.span else None,
    ),
    ChildSensorDescription(
        key="school_end",
        translation_key="school_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: _aware(s.span[1]) if s.span else None,
    ),
    ChildSensorDescription(
        key="pickup",
        translation_key="pickup",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda s: _aware(s.span[1]) if s.span else None,
        attrs_fn=_school_attrs,
    ),
)


def _entry_time(key: str, field: str) -> Callable[[dict[str, Any]], datetime | None]:
    return lambda c: _aware(c[key][field]) if c.get(key) else None


HUB_SENSORS: tuple[HubSensorDescription, ...] = (
    HubSensorDescription(
        key="earliest_start",
        translation_key="earliest_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_entry_time("earliest_start", "start"),
    ),
    HubSensorDescription(
        key="latest_end",
        translation_key="latest_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_entry_time("latest_end", "end"),
    ),
    HubSensorDescription(
        key="first_done",
        translation_key="first_done",
        value_fn=lambda c: c["first_done"]["name"] if c.get("first_done") else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SchoolPlannerConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the hub sensors and keep child sensors in sync with the store."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        SchoolPlannerHubSensor(coordinator, description) for description in HUB_SENSORS
    )

    known: set[str] = set()

    @callback
    def _add_new_children() -> None:
        new = [cid for cid in coordinator.data.children if cid not in known]
        known.update(new)
        async_add_entities(
            SchoolPlannerChildSensor(coordinator, cid, description)
            for cid in new
            for description in CHILD_SENSORS
        )

    _add_new_children()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_children))


class SchoolPlannerHubSensor(CoordinatorEntity[SchoolPlannerCoordinator], SensorEntity):
    """Sensor comparing all children."""

    _attr_has_entity_name = True
    entity_description: HubSensorDescription

    def __init__(
        self, coordinator: SchoolPlannerCoordinator, description: HubSensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"hub_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "hub")},
            name="School Planner",
            manufacturer="School Planner",
        )

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data.comparison)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        order = self.coordinator.data.comparison.get("pickup_order", [])
        return {
            "pickup_order": [
                {
                    "child": e["name"],
                    "ends": e["end"].strftime("%H:%M"),
                    "school": (e["school"] or {}).get("name"),
                }
                for e in order
            ]
        }


class SchoolPlannerChildSensor(CoordinatorEntity[SchoolPlannerCoordinator], SensorEntity):
    """Sensor for a single child."""

    _attr_has_entity_name = True
    entity_description: ChildSensorDescription

    def __init__(
        self,
        coordinator: SchoolPlannerCoordinator,
        child_id: str,
        description: ChildSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._child_id = child_id
        self._attr_unique_id = f"{child_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, child_id)},
            name=coordinator.data.children[child_id].name,
            manufacturer="School Planner",
            via_device=(DOMAIN, "hub"),
        )

    @property
    def _state(self) -> ChildState | None:
        return self.coordinator.data.children.get(self._child_id)

    @property
    def available(self) -> bool:
        return super().available and self._state is not None

    @property
    def native_value(self):
        return self.entity_description.value_fn(self._state) if self._state else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.entity_description.attrs_fn(self._state) if self._state else {}
