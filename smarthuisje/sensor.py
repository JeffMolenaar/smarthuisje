from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup Smarthuisje sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    # Voeg de sensor toe
    async_add_entities([
        SmarthuisjeSensor(
            coordinator,
            config_entry,
            key="message",
            name="sensor_name",
        )
    ])

class SmarthuisjeSensor(CoordinatorEntity, SensorEntity):
    """Definieer een Smarthuisje sensor."""

    def __init__(self, coordinator, config_entry, key, name):
        """Initialiseer de sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{key}"
        self._config_entry = config_entry
        self._update_device_info()

    def _update_device_info(self):
        """Update device_info met gegevens uit de coordinator."""
        # Gebruik standaardwaarden als er nog geen data is ontvangen
        model = self.coordinator.data.get("device", "Smarthuisje v1")
        sw_version = self.coordinator.data.get("software_version", "1.0")

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": f"Smarthuisje {self._config_entry.data['name']}",
            "manufacturer": "Smarthuisje.nl",
            "model": model,
            "sw_version": sw_version,
        }

    @property
    def native_value(self):
        """Geef de waarde van de sensor terug."""
        message = self.coordinator.data.get(self._key, "Geen gegevens")
        _LOGGER.debug(f"Ontvangen message: {message}")
        return message

    @property
    def name(self):
        """Retourneer de naam van de sensor."""
        # Gebruik de naam uit de coordinator-data, als beschikbaar
        data = self.coordinator.data.get(self._attr_name, "Smarthuisje Sensor")
        _LOGGER.debug(f"Ontvangen name: {data}")
        return data
