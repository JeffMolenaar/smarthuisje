from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import websockets
import json
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)

class SmarthuisjeWebSocketCoordinator(DataUpdateCoordinator):
    """Beheer de WebSocket-verbinding met Smarthuisje."""

    def __init__(self, hass, host, port):
        """Initialiseer de WebSocket-coordinator."""
        super().__init__(hass, _LOGGER, name="Smarthuisje WebSocket Coordinator")
        self._host = host
        self._port = port
        self._url = f"ws://{self._host}:{self._port}"
        self.data = {}
        self._reconnect_delay = 5  # Wacht 5 seconden voor reconnect
        self._task = None          # Opslaan van de WebSocket-taak
        self._current_bool = None  # Houd de huidige boolean-status bij

    async def async_start(self):
        """Start de WebSocket-verbinding."""
        if self._task:
            _LOGGER.warning("WebSocket-coördinator is al gestart.")
            return

        # Start een achtergrondtaak
        self._task = asyncio.create_task(self._run_websocket())

    async def async_stop(self):
        """Stop de WebSocket-verbinding."""
        if self._task:
            _LOGGER.info("WebSocket-coördinator stoppen...")
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                _LOGGER.info("WebSocket-coördinator succesvol gestopt.")
            self._task = None

    async def _run_websocket(self):
        """Intern proces om de WebSocket-verbinding te beheren."""
        while True:
            try:
                _LOGGER.info(f"Verbinden met WebSocket: {self._url}")
                async with websockets.connect(
                    self._url, 
                    ping_interval=20,  # Stuur elke 20 seconden een ping
                    ping_timeout=10,   # Timeout als geen antwoord binnen 10 seconden
                ) as websocket:
                    _LOGGER.info(f"Succesvolle verbinding met WebSocket: {self._url}")
                    while True:
                        # Ontvang berichten en debug de ontvangen data
                        message = await websocket.recv()
                        _LOGGER.debug(f"Ontvangen bericht: {message}")  # Voeg dit debug-bericht toe
                        
                        new_data = json.loads(message)

                        # Controleer of de boolean is veranderd
                        new_bool = new_data.get("message")
                        if new_bool != self._current_bool:
                            self._current_bool = new_bool
                            self.data = new_data
                            self.async_set_updated_data(self.data)
                            _LOGGER.debug(f"Boolean gewijzigd: {self.data}")
                        else:
                            _LOGGER.debug("Geen wijziging in boolean, geen update nodig.")
            except websockets.ConnectionClosed as e:
                _LOGGER.warning(f"WebSocket-verbinding gesloten: {e}. Opnieuw verbinden...")
                await asyncio.sleep(self._reconnect_delay)
            except Exception as e:
                _LOGGER.error(f"WebSocket-fout: {e}. Opnieuw proberen...")
                await asyncio.sleep(self._reconnect_delay)
