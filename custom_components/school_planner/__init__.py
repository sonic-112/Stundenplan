"""School Planner: timetables for several children."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import voluptuous as vol

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from .const import CARD_FILE, DOMAIN, URL_BASE
from .coordinator import SchoolPlannerCoordinator
from .schemas import LESSON_SCHEMA
from .store import PlannerStore
from .websocket_api import async_register_websocket_api

PLATFORMS = [Platform.SENSOR]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

SET_LESSONS_SCHEMA = vol.Schema(
    {
        vol.Required("child"): cv.string,
        vol.Required("weekday"): vol.In(WEEKDAY_KEYS),
        vol.Required("lessons"): vol.All(cv.ensure_list, [LESSON_SCHEMA]),
    }
)


@dataclass
class RuntimeData:
    """Objects shared between platforms."""

    store: PlannerStore
    coordinator: SchoolPlannerCoordinator


type SchoolPlannerConfigEntry = ConfigEntry[RuntimeData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the frontend card, the websocket API and the services."""
    integration = await async_get_integration(hass, DOMAIN)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(URL_BASE, str(Path(__file__).parent / "frontend"), False)]
    )
    add_extra_js_url(hass, f"{URL_BASE}/{CARD_FILE}?v={integration.version}")
    async_register_websocket_api(hass)

    async def set_lessons(call: ServiceCall) -> None:
        entries = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            raise ServiceValidationError("School Planner is not set up")
        store = entries[0].runtime_data.store
        wanted = call.data["child"].strip().casefold()
        for child_id, child in store.data["children"].items():
            if child["name"].casefold() == wanted or child_id == call.data["child"]:
                store.set_day(
                    child_id,
                    str(WEEKDAY_KEYS.index(call.data["weekday"])),
                    call.data["lessons"],
                )
                return
        raise ServiceValidationError(f"Unknown child: {call.data['child']}")

    hass.services.async_register(DOMAIN, "set_lessons", set_lessons, SET_LESSONS_SCHEMA)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SchoolPlannerConfigEntry) -> bool:
    """Set up School Planner from a config entry."""
    store = PlannerStore(hass)
    await store.async_load()
    coordinator = SchoolPlannerCoordinator(hass, entry, store)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = RuntimeData(store=store, coordinator=coordinator)

    @callback
    def _store_changed() -> None:
        coordinator.async_set_updated_data(coordinator.compute())
        registry = dr.async_get(hass)
        known = set(store.data["children"])
        for device in dr.async_entries_for_config_entry(registry, entry.entry_id):
            for domain, ident in device.identifiers:
                if domain == DOMAIN and ident != "hub" and ident not in known:
                    registry.async_update_device(
                        device.id, remove_config_entry_id=entry.entry_id
                    )

    @callback
    def _tick(_now) -> None:
        coordinator.async_set_updated_data(coordinator.compute())

    entry.async_on_unload(store.async_add_listener(_store_changed))
    entry.async_on_unload(async_track_time_change(hass, _tick, second=0))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SchoolPlannerConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
