import asyncio
import logging
from dataclasses import dataclass

import aiohttp
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.llm import APIInstance, LLMContext, ToolInput

from .const import (
    API_PROMPT,
    BRAVE_SEARCH_URL,
    DEFAULT_RESULT_COUNT,
    DOMAIN,
    MAX_RESULT_COUNT,
    MIN_RESULT_COUNT,
    REQUEST_TIMEOUT_SECONDS,
    TOOL_DESCRIPTION,
    TOOL_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_search_brave(
    hass: HomeAssistant, api_key: str, query: str, count: int
) -> list[dict[str, str]]:
    """
    Call the Brave Web Search API and extract the top results.

    Shared by the `brave_search` llm.Tool (for HA's own Assist LLM API) and
    the plain `brave_search.search` service (for everything else: scripts,
    automations, and external callers like another assistant's generic
    "call any Home Assistant service" tool).

    param hass: The Home Assistant instance, used to get the shared aiohttp session.
    param api_key: The Brave Search API key stored for this integration.
    param query: The search query to send to Brave.
    param count: The maximum number of results to return.

    :return: A list of compact result dicts with title, url and description.
    """
    session = async_get_clientsession(hass)
    headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
    params = {"q": query, "count": str(count)}

    async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
        response = await session.get(BRAVE_SEARCH_URL, headers=headers, params=params)

    if response.status == 429:
        raise RuntimeError("Brave Search rate limit exceeded.")
    if response.status in (401, 403):
        raise RuntimeError("Brave Search API key was rejected.")
    if response.status != 200:
        raise RuntimeError(f"Brave Search returned HTTP {response.status}.")

    payload = await response.json()
    web_results = payload.get("web", {}).get("results", [])

    return [
        {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "description": result.get("description", ""),
        }
        for result in web_results[:count]
    ]


SEARCH_PARAMETERS_SCHEMA = vol.Schema(
    {
        vol.Required("query"): str,
        vol.Optional("count", default=DEFAULT_RESULT_COUNT): vol.All(
            int, vol.Range(min=MIN_RESULT_COUNT, max=MAX_RESULT_COUNT)
        ),
    }
)


class BraveSearchTool(llm.Tool):
    """An llm Tool that searches the public internet using the Brave Search API."""

    name = TOOL_NAME
    description = TOOL_DESCRIPTION
    integration = DOMAIN
    parameters = SEARCH_PARAMETERS_SCHEMA

    async def async_call(
        self, hass: HomeAssistant, tool_input: ToolInput, llm_context: LLMContext
    ):
        """
        Run a Brave Search for the query requested by the LLM.

        param hass: The Home Assistant instance.
        param tool_input: The validated tool arguments, with "query" and "count".
        param llm_context: The context of the conversation calling this tool.

        :return: A dict with either the compact search results or an error message.
        """
        api_keys = list(hass.data.get(DOMAIN, {}).values())
        if not api_keys:
            return {"error": "Brave Search is not configured in Home Assistant."}

        query = tool_input.tool_args["query"]
        count = tool_input.tool_args.get("count", DEFAULT_RESULT_COUNT)

        try:
            results = await async_search_brave(hass, api_keys[0], query, count)
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as error:
            _LOGGER.warning("Brave Search tool call failed: %s", error)
            return {"error": f"Web search failed: {error}"}

        if not results:
            return {"results": [], "message": "No results found."}

        return {"results": results}


@dataclass(slots=True, kw_only=True)
class BraveSearchAPI(llm.API):
    """LLM API that exposes the Brave Search tool to conversation agents.

    Registered via `llm.async_register_api` so it shows up as a selectable
    (and combinable, alongside "Assist") LLM API in a conversation agent's
    configuration, per homeassistant/helpers/llm.py's `async_get_api`, which
    merges multiple selected API ids via `MergedAPI`.
    """

    async def async_get_api_instance(self, llm_context: LLMContext) -> APIInstance:
        """Return the instance of this API."""
        return APIInstance(
            api=self,
            api_prompt=API_PROMPT,
            llm_context=llm_context,
            tools=[BraveSearchTool()],
        )
