"""Reaper switch."""
import json
import logging
from typing import Any, cast

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ReaperDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Reaper switch."""
    coordinator: ReaperDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([ReaperRecordingSwitch(hass, coordinator)], False)
    async_add_entities([ReaperMetronomeSwitch(hass, coordinator)], False)
    async_add_entities([ReaperRepeatSwitch(hass, coordinator)], False)


class ReaperSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a generic Reaper switch entity."""

    coordinator: ReaperDataUpdateCoordinator

    def __init__(self, hass, coordinator: ReaperDataUpdateCoordinator):
        """Initialize the switch."""
        super().__init__(coordinator)

        self.status = json.loads(coordinator.data)
        self.hass = hass
        self._name = ""
        self._unique_id = ""
        self._icon = ""

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def icon(self):
        """Return the icon of the switch."""
        return self._icon

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.hostname)},
            "name": self.coordinator.hostname,
            "manufacturer": "Cockos Reaper",
        }

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._unique_id

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update Reaper entity."""
        self.status = json.loads(self.coordinator.data)
        await self.coordinator.async_request_refresh()


class ReaperRecordingSwitch(ReaperSwitch):
    """Representation of a Reaper recording switch."""

    def __init__(self, hass, coordinator):
        """Initialize the recording switch."""
        super().__init__(hass, coordinator)
        self._name = "Recording"
        self._unique_id = f"{coordinator.hostname}-recording"
        self._icon = "mdi:circle"

    @property
    def is_on(self):
        """Return if switch is on."""
        _LOGGER.debug(self.status.get("play_state"))
        if self.status:
            return self.status.get("play_state") == "recording"

    async def async_turn_on(self, **kwargs):
        """Turn on the recording."""
        await self.coordinator.reaperdaw.record()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the recording."""
        await self.coordinator.reaperdaw.stop()
        self.async_write_ha_state()


class ReaperMetronomeSwitch(ReaperSwitch):
    """Representation of a Reaper metronome switch."""

    def __init__(self, hass, coordinator):
        """Initialize the metronome switch."""
        super().__init__(hass, coordinator)
        self._name = "Metronome"
        self._unique_id = f"{coordinator.hostname}-metronome"
        self._icon = "mdi:metronome"

    @property
    def is_on(self):
        """Return if metronome is on."""
        _LOGGER.debug(self.status.get("metronome"))
        return self.status.get("metronome") == True

    async def async_turn_on(self, **kwargs):
        """Turn on metronome."""
        await self.coordinator.reaperdaw.enableMetronome()
        self.async_write_ha_state()
        _LOGGER.debug(self.status.get("metronome"))

    async def async_turn_off(self, **kwargs):
        """Turn off metronome."""
        await self.coordinator.reaperdaw.disableMetronome()
        self.async_write_ha_state()
        _LOGGER.debug(self.status.get("metronome"))


class ReaperRepeatSwitch(ReaperSwitch):
    """Representation of a Reaper repeat switch."""

    def __init__(self, hass, coordinator):
        """Intialize the repeat switch."""
        super().__init__(hass, coordinator)
        self._name = "Repeat"
        self._unique_id = f"{coordinator.hostname}-repeat"
        self._icon = "mdi:repeat"

    @property
    def is_on(self):
        """Return if repeat is on."""
        _LOGGER.debug(self.status.get("repeat"))
        return self.status.get("repeat") == True

    async def async_turn_on(self, **kwargs):
        """Turn on repeat."""
        await self.coordinator.reaperdaw.toggleRepeat()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off repeat."""
        await self.coordinator.reaperdaw.toggleRepeat()
        self.async_write_ha_state()