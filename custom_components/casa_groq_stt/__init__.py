from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import GroqAuthError, GroqClient, GroqError


async def async_setup_entry(hass, entry):
    client = GroqClient(async_get_clientsession(hass), entry.data[CONF_API_KEY])
    try:
        await client.validate()
    except GroqAuthError as err:
        raise ConfigEntryAuthFailed("Clave de Groq no válida") from err
    except GroqError as err:
        raise ConfigEntryNotReady("Groq no disponible") from err
    entry.runtime_data = client
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.STT])
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, [Platform.STT])
