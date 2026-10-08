from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .const import API_NAME, DOMAIN
from .llm import BraveSearchAPI


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up the Brave Search integration from a config entry.

    param hass: The Home Assistant instance.
    param entry: The config entry holding the Brave Search API key.

    :return: True once the API key is stored and the Brave Search LLM API
        has been registered for conversation agents to select.
    """
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data[CONF_API_KEY]

    unregister = llm.async_register_api(
        hass, BraveSearchAPI(hass=hass, id=DOMAIN, name=API_NAME)
    )
    entry.async_on_unload(unregister)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a Brave Search config entry.

    param hass: The Home Assistant instance.
    param entry: The config entry being unloaded.

    :return: True once the stored API key has been removed, making the llm
        tool stop being offered to conversation agents.
    """
    hass.data[DOMAIN].pop(entry.entry_id, None)
    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
    return True
