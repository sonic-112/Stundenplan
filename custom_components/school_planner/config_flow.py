"""Config and options flow for School Planner."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DEFAULT_HOMEWARD,
    DEFAULT_LESSON_STYLE,
    DEFAULT_PICKUP_LABEL,
    DOMAIN,
    HOMEWARD,
    LESSON_STYLES,
    THEMES,
)


def _hex(rgb: list[int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*(int(v) for v in rgb))


def _rgb(value: str | None) -> list[int]:
    value = (value or "#4c8df6").lstrip("#")
    return [int(value[i : i + 2], 16) for i in (0, 2, 4)]


class SchoolPlannerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step setup; all data is maintained afterwards."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="School Planner", data={})
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        return SchoolPlannerOptionsFlow()


class SchoolPlannerOptionsFlow(OptionsFlow):
    """Manage children, schools and design."""

    _target: str | None = None

    @property
    def _store(self):
        return self.config_entry.runtime_data.store

    def _finish(self) -> Any:
        return self.async_create_entry(data=dict(self.config_entry.options))

    def _school_options(self) -> list[selector.SelectOptionDict]:
        return [
            selector.SelectOptionDict(value=sid, label=s["name"])
            for sid, s in self._store.data["schools"].items()
        ]

    def _pick(self, kind: str) -> vol.Schema:
        items = self._store.data[kind]
        return vol.Schema(
            {
                vol.Required("target"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=i, label=v["name"])
                            for i, v in items.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "add_child",
                "edit_child",
                "remove_child",
                "add_school",
                "edit_school",
                "remove_school",
                "settings",
            ],
        )

    # -- children ---------------------------------------------------------

    def _child_schema(self) -> vol.Schema:
        fields: dict[Any, Any] = {
            vol.Required("name"): str,
            vol.Required("color"): selector.ColorRGBSelector(),
        }
        if self._store.data["schools"]:
            fields[vol.Optional("school_id")] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=self._school_options(),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
        fields[vol.Required("homeward")] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=HOMEWARD,
                translation_key="homeward",
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )
        fields[vol.Optional("holiday_entity")] = selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["calendar", "binary_sensor", "input_boolean", "schedule"]
            )
        )
        return vol.Schema(fields)

    async def _child_form(self, step: str, user_input, child_id: str | None):
        if user_input is not None:
            fields = {
                "name": user_input["name"].strip(),
                "color": _hex(user_input["color"]),
                "school_id": user_input.get("school_id"),
                "holiday_entity": user_input.get("holiday_entity"),
                "homeward": user_input.get("homeward", DEFAULT_HOMEWARD),
            }
            self._store.upsert_child(child_id, fields)
            return self._finish()
        suggested: dict[str, Any] = {"color": _rgb(None), "homeward": DEFAULT_HOMEWARD}
        if child_id:
            child = self._store.data["children"][child_id]
            suggested = {
                "name": child["name"],
                "color": _rgb(child["color"]),
                "school_id": child.get("school_id"),
                "holiday_entity": child.get("holiday_entity"),
                "homeward": child.get("homeward", DEFAULT_HOMEWARD),
            }
        return self.async_show_form(
            step_id=step,
            data_schema=self.add_suggested_values_to_schema(self._child_schema(), suggested),
        )

    async def async_step_add_child(self, user_input=None):
        return await self._child_form("add_child", user_input, None)

    async def async_step_edit_child(self, user_input=None):
        if not self._store.data["children"]:
            return self.async_abort(reason="no_children")
        if user_input is None:
            return self.async_show_form(step_id="edit_child", data_schema=self._pick("children"))
        self._target = user_input["target"]
        return await self.async_step_edit_child_details()

    async def async_step_edit_child_details(self, user_input=None):
        return await self._child_form("edit_child_details", user_input, self._target)

    async def async_step_remove_child(self, user_input=None):
        if not self._store.data["children"]:
            return self.async_abort(reason="no_children")
        if user_input is None:
            return self.async_show_form(step_id="remove_child", data_schema=self._pick("children"))
        self._store.delete_child(user_input["target"])
        return self._finish()

    # -- schools ----------------------------------------------------------

    def _school_schema(self) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Optional("address"): str,
                vol.Optional("zone"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="zone")
                ),
            }
        )

    async def _school_form(self, step: str, user_input, school_id: str | None):
        if user_input is not None:
            self._store.upsert_school(
                school_id,
                {
                    "name": user_input["name"].strip(),
                    "address": user_input.get("address", ""),
                    "zone": user_input.get("zone"),
                },
            )
            return self._finish()
        suggested = self._store.data["schools"].get(school_id or "", {})
        return self.async_show_form(
            step_id=step,
            data_schema=self.add_suggested_values_to_schema(self._school_schema(), suggested),
        )

    async def async_step_add_school(self, user_input=None):
        return await self._school_form("add_school", user_input, None)

    async def async_step_edit_school(self, user_input=None):
        if not self._store.data["schools"]:
            return self.async_abort(reason="no_schools")
        if user_input is None:
            return self.async_show_form(step_id="edit_school", data_schema=self._pick("schools"))
        self._target = user_input["target"]
        return await self.async_step_edit_school_details()

    async def async_step_edit_school_details(self, user_input=None):
        return await self._school_form("edit_school_details", user_input, self._target)

    async def async_step_remove_school(self, user_input=None):
        if not self._store.data["schools"]:
            return self.async_abort(reason="no_schools")
        if user_input is None:
            return self.async_show_form(step_id="remove_school", data_schema=self._pick("schools"))
        self._store.delete_school(user_input["target"])
        return self._finish()

    # -- design -----------------------------------------------------------

    async def async_step_settings(self, user_input=None):
        settings = self._store.data["settings"]
        if user_input is not None:
            accent = user_input.get("accent")
            self._store.update_settings(
                {
                    "theme": user_input["theme"],
                    "accent": _hex(accent) if accent else None,
                    "pickup_label": user_input["pickup_label"].strip() or DEFAULT_PICKUP_LABEL,
                    "sidebar": user_input["sidebar"],
                    "lesson_style": user_input["lesson_style"],
                }
            )
            return self._finish()
        suggested = {
            "theme": settings["theme"],
            "pickup_label": settings.get("pickup_label", DEFAULT_PICKUP_LABEL),
            "sidebar": settings.get("sidebar", True),
            "lesson_style": settings.get("lesson_style", DEFAULT_LESSON_STYLE),
        }
        if settings.get("accent"):
            suggested["accent"] = _rgb(settings["accent"])
        schema = vol.Schema(
            {
                vol.Required("theme"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=THEMES,
                        translation_key="theme",
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Optional("accent"): selector.ColorRGBSelector(),
                vol.Required("pickup_label"): str,
                vol.Required("lesson_style"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=LESSON_STYLES,
                        translation_key="lesson_style",
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Required("sidebar"): selector.BooleanSelector(),
            }
        )
        return self.async_show_form(
            step_id="settings",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
        )
