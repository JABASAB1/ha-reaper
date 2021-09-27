"""Test sensor of Reaper integration."""
from datetime import timedelta
import json
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
    load_fixture,
)

from custom_components.reaper.const import (
    CONF_HOSTNAME,
    CONF_PORT,
    CONF_UPDATE_INTERVAL,
    CONF_USERNAME,
    CONF_PASSWORD,
    ATTRIBUTION,
    DOMAIN,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.util.dt import utcnow


async def test_sensor(hass, bypass_get_data):
    """Test sensor."""
    registry = er.async_get(hass)

    entry = MockConfigEntry(domain=DOMAIN, data={
        CONF_HOSTNAME: "192.168.0.5",
        CONF_PORT: 9999,
        CONF_USERNAME: "",
        CONF_PASSWORD: "",
        CONF_UPDATE_INTERVAL: 30,
    })
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.number_of_tracks")

    assert state
    assert state.state == "4"
    assert state.attributes.get("attribution") == ATTRIBUTION
    assert state.attributes.get("icon") == "mdi:audio-input-stereo-minijack"
    assert state.attributes.get("device_class") == "reaper__number_of_tracks"

    entry = registry.async_get("sensor.number_of_tracks")

    assert entry
    assert entry.unique_id == "192.168.0.5-number_of_tracks"


async def test_state_update(hass, bypass_get_data):
    """Ensure the sensor state changes after updating the data."""
    entry = MockConfigEntry(domain=DOMAIN, data={
        CONF_HOSTNAME: "192.168.0.5",
        CONF_PORT: 8080,
        CONF_USERNAME: "admin",
        CONF_PASSWORD: "pass",
        CONF_UPDATE_INTERVAL: 60,
    })
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.number_of_tracks")

    assert state
    assert state.state == "4"

    future = utcnow() + timedelta(seconds=30)

    status = json.loads(load_fixture("reaper_status_data.json"))
    status["number_of_tracks"] = 8

    with patch(
        "custom_components.reaper.Reaper.getStatus", return_value=status
    ):
        async_fire_time_changed(hass, future)
        await hass.async_block_till_done()

        state = hass.states.get("sensor.number_of_tracks")
        assert state
        assert state.state == "4"
