from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .coordinator import SmarthuisjeWebSocketCoordinator
from .const import DOMAIN

async def async_setup_entry(hass, config_entry):
    """Setup vanuit config entry."""
    # Maak de WebSocket-coordinator aan
    coordinator = SmarthuisjeWebSocketCoordinator(
        hass,
        config_entry.data["host"],
        config_entry.data["port"],
    )

    # Start de WebSocket-verbinding
    await coordinator.async_start()

    # Sla de coordinator op
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {"coordinator": coordinator}

    # Voeg de platforms toe (bijvoorbeeld sensors)
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, ["sensor"]
    )

    # Stop de WebSocket-coordinator
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
