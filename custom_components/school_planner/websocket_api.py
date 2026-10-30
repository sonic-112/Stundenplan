"""Websocket API used by the dashboard card."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .schemas import CHILD_FIELDS, OVERRIDE_FIELDS, SCHOOL_FIELDS, SETTINGS_FIELDS, iso_date


def _store(hass: HomeAssistant):
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    return entries[0].runtime_data.store if entries else None


def _require_store(func):
    """Reply with an error when the integration is not set up."""

    def wrapper(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
        store = _store(hass)
        if store is None:
            connection.send_error(msg["id"], "not_loaded", "School Planner is not set up")
            return
        func(hass, connection, msg, store)

    return wrapper


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register all commands."""
    for handler in (
        ws_get_data,
        ws_save_child,
        ws_delete_child,
        ws_save_school,
        ws_delete_school,
        ws_save_settings,
        ws_save_override,
        ws_clear_override,
    ):
        websocket_api.async_register_command(hass, handler)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/get_data"})
@callback
@_require_store
def ws_get_data(hass, connection, msg, store) -> None:
    """Return everything the card needs."""
    connection.send_result(msg["id"], store.data)


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_child",
        vol.Optional("child_id"): str,
        **CHILD_FIELDS,
    }
)
@websocket_api.require_admin
@callback
@_require_store
def ws_save_child(hass, connection, msg, store) -> None:
    """Create or update a child."""
    fields = {k: v for k, v in msg.items() if k in {str(f) for f in CHILD_FIELDS}}
    try:
        child_id = store.upsert_child(msg.get("child_id"), fields)
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown child")
        return
    connection.send_result(msg["id"], {"child_id": child_id})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete_child", vol.Required("child_id"): str}
)
@websocket_api.require_admin
@callback
@_require_store
def ws_delete_child(hass, connection, msg, store) -> None:
    """Delete a child."""
    try:
        store.delete_child(msg["child_id"])
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown child")
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_school",
        vol.Optional("school_id"): str,
        **SCHOOL_FIELDS,
    }
)
@websocket_api.require_admin
@callback
@_require_store
def ws_save_school(hass, connection, msg, store) -> None:
    """Create or update a school."""
    fields = {k: v for k, v in msg.items() if k in {str(f) for f in SCHOOL_FIELDS}}
    try:
        school_id = store.upsert_school(msg.get("school_id"), fields)
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown school")
        return
    connection.send_result(msg["id"], {"school_id": school_id})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete_school", vol.Required("school_id"): str}
)
@websocket_api.require_admin
@callback
@_require_store
def ws_delete_school(hass, connection, msg, store) -> None:
    """Delete a school."""
    try:
        store.delete_school(msg["school_id"])
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown school")
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/save_settings", **SETTINGS_FIELDS}
)
@websocket_api.require_admin
@callback
@_require_store
def ws_save_settings(hass, connection, msg, store) -> None:
    """Update global settings."""
    store.update_settings({k: v for k, v in msg.items() if k in {str(f) for f in SETTINGS_FIELDS}})
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_override",
        vol.Required("child_id"): str,
        **OVERRIDE_FIELDS,
    }
)
@websocket_api.require_admin
@callback
@_require_store
def ws_save_override(hass, connection, msg, store) -> None:
    """Change a single date for one child (substitution, cancelled lessons, day off)."""
    try:
        store.set_override(
            msg["child_id"], msg["date"], off=msg["off"], lessons=msg["lessons"]
        )
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown child")
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/clear_override",
        vol.Required("child_id"): str,
        vol.Required("date"): iso_date,
    }
)
@websocket_api.require_admin
@callback
@_require_store
def ws_clear_override(hass, connection, msg, store) -> None:
    """Return a date to the regular timetable."""
    try:
        store.clear_override(msg["child_id"], msg["date"])
    except KeyError:
        connection.send_error(msg["id"], "not_found", "Unknown child")
        return
    connection.send_result(msg["id"])
