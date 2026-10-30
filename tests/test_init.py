"""Integration-level tests."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.setup import async_setup_component

from custom_components.school_planner.const import DOMAIN


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_children_get_entities_and_cleanup(hass: HomeAssistant) -> None:
    entry = await _setup(hass)
    store = entry.runtime_data.store
    child_id = store.upsert_child(None, {"name": "Emma"})
    store.set_day(
        child_id,
        "0",
        [{"start": "00:00", "end": "23:59", "subject": "Maths", "room": "", "teacher": ""}],
    )
    await hass.async_block_till_done()

    registry = dr.async_get(hass)
    assert registry.async_get_device(identifiers={(DOMAIN, child_id)})
    assert len(hass.states.async_entity_ids("sensor")) == 5 + 3

    store.delete_child(child_id)
    await hass.async_block_till_done()
    assert registry.async_get_device(identifiers={(DOMAIN, child_id)}) is None


async def test_set_lessons_service(hass: HomeAssistant) -> None:
    entry = await _setup(hass)
    store = entry.runtime_data.store
    child_id = store.upsert_child(None, {"name": "Emma"})
    await hass.services.async_call(
        DOMAIN,
        "set_lessons",
        {
            "child": "emma",
            "weekday": "tue",
            "lessons": [{"start": "08:00", "end": "08:45", "subject": "Art"}],
        },
        blocking=True,
    )
    assert store.data["children"][child_id]["timetable"]["1"][0]["subject"] == "Art"
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "set_lessons",
            {"child": "nobody", "weekday": "mon", "lessons": []},
            blocking=True,
        )


async def test_websocket_get_data(hass: HomeAssistant, hass_ws_client) -> None:
    await _setup(hass)
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/save_child", "name": "Emma"})
    assert (await client.receive_json())["success"]
    await client.send_json({"id": 2, "type": f"{DOMAIN}/get_data"})
    result = (await client.receive_json())["result"]
    assert [c["name"] for c in result["children"].values()] == ["Emma"]
