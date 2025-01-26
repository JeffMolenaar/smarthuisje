import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SmarthuisjeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Smarthuisje Config Flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Controleer of het apparaat al bestaat
                existing_entries = [
                    entry.data["host"]
                    for entry in self._async_current_entries()
                ]
                if user_input["host"] in existing_entries:
                    errors["base"] = "device_exists"
                else:
                    # Test de verbinding
                    await self._test_connection(user_input["host"], user_input["port"])

                    # Maak een nieuwe configuratie-entry aan
                    return self.async_create_entry(
                        title=f"{user_input['name']} ({user_input['host']})",
                        data=user_input,
                    )
            except Exception:
                errors["base"] = "cannot_connect"

        # Vraag de gebruiker om de host en poort
        data_schema = vol.Schema({
            vol.Required("name", default="Smarthuisje"): str,
            vol.Required("host"): str,
            vol.Optional("port", default=8080): int,  # Standaardpoort ingesteld op 8080
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _test_connection(self, host, port):
        """Test de verbinding met een WebSocket."""
        import websockets
        uri = f"ws://{host}:{port}"
        try:
            async with websockets.connect(uri):
                pass
        except Exception as e:
            raise e
