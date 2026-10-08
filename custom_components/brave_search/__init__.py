import asyncio

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm

from .brave_llm import BraveSearchAPI, SEARCH_PARAMETERS_SCHEMA, async_search_brave
from .const import API_NAME, DEFAULT_RESULT_COUNT, DOMAIN, SERVICE_SEARCH


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up the Brave Search integration from a config entry.

    param hass: The Home Assistant instance.
    param entry: The config entry holding the Brave Search API key.

    :return: True once the API key is stored, the Brave Search LLM API is
        registered for conversation agents to select, and the plain
        `brave_search.search` service is registered for any other caller
        (scripts, automations, or an external assistant's generic
        "call a Home Assistant service" tool).
    """
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data[CONF_API_KEY]

    unregister_api = llm.async_register_api(
        hass, BraveSearchAPI(hass=hass, id=DOMAIN, name=API_NAME)
    )
    entry.async_on_unload(unregister_api)

    async def async_handle_search(call: ServiceCall) -> ServiceResponse:
        """Run a Brave Search for the `brave_search.search` service call."""
        api_keys = list(hass.data.get(DOMAIN, {}).values())
        if not api_keys:
            raise HomeAssistantError("Brave Search is not configured.")

        try:
            results = await async_search_brave(
                hass,
                api_keys[0],
                call.data["query"],
                call.data.get("count", DEFAULT_RESULT_COUNT),
            )
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as error:
            raise HomeAssistantError(str(error)) from error

        return {"results": results}

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH,
        async_handle_search,
        schema=SEARCH_PARAMETERS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, SERVICE_SEARCH))

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
