"""Integration-level tests."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

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


async def test_day_override_service_and_state(hass: HomeAssistant) -> None:
    entry = await _setup(hass)
    store = entry.runtime_data.store
    coordinator = entry.runtime_data.coordinator
    child_id = store.upsert_child(None, {"name": "Emma"})
    today = dt_util.now()
    store.set_day(
        child_id,
        str(today.weekday()),
        [{"start": "00:00", "end": "23:59", "subject": "Maths", "room": "", "teacher": ""}],
    )
    await hass.async_block_till_done()
    assert coordinator.data.children[child_id].span is not None

    await hass.services.async_call(
        DOMAIN,
        "set_day_override",
        {"child": "Emma", "date": today.date().isoformat(), "off": True},
        blocking=True,
    )
    await hass.async_block_till_done()
    state = coordinator.data.children[child_id]
    assert state.free and state.changed_today and state.span is None
    # the regular plan is untouched
    assert store.data["children"][child_id]["timetable"][str(today.weekday())]

    await hass.services.async_call(
        DOMAIN,
        "clear_day_override",
        {"child": "Emma", "date": today.date().isoformat()},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert coordinator.data.children[child_id].span is not None


async def test_override_without_lessons_counts_as_off_and_old_ones_are_pruned(
    hass: HomeAssistant,
) -> None:
    entry = await _setup(hass)
    store = entry.runtime_data.store
    child_id = store.upsert_child(None, {"name": "Emma"})
    store.set_override(child_id, "2099-01-05", off=False, lessons=[])
    assert store.data["children"][child_id]["overrides"]["2099-01-05"]["off"] is True
    store.set_override(child_id, "2001-01-01", off=True, lessons=[])
    assert "2001-01-01" not in store.data["children"][child_id]["overrides"]


async def test_websocket_override_and_child_defaults(hass: HomeAssistant, hass_ws_client) -> None:
    await _setup(hass)
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/save_child", "name": "Emma"})
    child_id = (await client.receive_json())["result"]["child_id"]
    await client.send_json(
        {
            "id": 2,
            "type": f"{DOMAIN}/save_override",
            "child_id": child_id,
            "date": "2099-03-02",
            "lessons": [{"start": "08:00", "end": "08:45", "subject": "Art"}],
        }
    )
    assert (await client.receive_json())["success"]
    await client.send_json({"id": 3, "type": f"{DOMAIN}/get_data"})
    child = (await client.receive_json())["result"]["children"][child_id]
    assert child["homeward"] == "pickup"
    assert child["overrides"]["2099-03-02"]["lessons"][0]["subject"] == "Art"
    await client.send_json(
        {"id": 4, "type": f"{DOMAIN}/clear_override", "child_id": child_id, "date": "2099-03-02"}
    )
    assert (await client.receive_json())["success"]
    await client.send_json(
        {"id": 5, "type": f"{DOMAIN}/save_override", "child_id": "nope", "date": "2099-03-02", "off": True}
    )
    assert (await client.receive_json())["error"]["code"] == "not_found"
    await client.send_json(
        {"id": 6, "type": f"{DOMAIN}/save_override", "child_id": child_id, "date": "kein-datum"}
    )
    assert not (await client.receive_json())["success"]


async def test_existing_data_gets_new_defaults(hass: HomeAssistant, hass_storage) -> None:
    """Data written by version 0.1.x has no homeward, overrides or pickup label."""
    hass_storage["school_planner"] = {
        "version": 1,
        "minor_version": 1,
        "key": "school_planner",
        "data": {
            "settings": {"theme": "night", "accent": None},
            "schools": {"s1": {"name": "School", "address": "", "zone": None}},
            "children": {
                "c1": {
                    "name": "Emma",
                    "color": "#4C8DF6",
                    "school_id": "s1",
                    "holiday_entity": None,
                    "timetable": {"0": [{"start": "08:00", "end": "08:45", "subject": "Art"}]},
                }
            },
        },
    }
    entry = await _setup(hass)
    data = entry.runtime_data.store.data
    assert data["children"]["c1"]["homeward"] == "pickup"
    assert data["children"]["c1"]["overrides"] == {}
    assert data["settings"]["pickup_label"] == "Abholung"
    assert data["settings"]["theme"] == "night"
    assert data["children"]["c1"]["timetable"]["0"][0]["subject"] == "Art"


def test_services_yaml_matches_registered_services() -> None:
    """hassfest rejects non-string keys such as an unquoted ``off`` (YAML reads it as False)."""
    import pathlib

    import yaml

    path = pathlib.Path(__file__).parent.parent / "custom_components" / "school_planner" / "services.yaml"
    described = yaml.safe_load(path.read_text())
    assert set(described) == {"set_lessons", "set_day_override", "clear_day_override"}
    for service, body in described.items():
        assert all(isinstance(key, str) for key in body["fields"]), service
