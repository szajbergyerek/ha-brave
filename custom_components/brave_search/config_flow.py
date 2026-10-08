import asyncio

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BRAVE_SEARCH_URL, DOMAIN, REQUEST_TIMEOUT_SECONDS

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class CannotConnect(HomeAssistantError):
    """Raised when the Brave Search API cannot be reached."""


class InvalidAuth(HomeAssistantError):
    """Raised when the given Brave Search API key is rejected."""


async def _async_validate_api_key(hass: HomeAssistant, api_key: str) -> None:
    """
    Validate a Brave Search API key with a lightweight test call.

    param hass: The Home Assistant instance, used to get the shared aiohttp session.
    param api_key: The Brave Search API key to validate.

    :return: None if the key is valid.
    """
    session = async_get_clientsession(hass)
    headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
    params = {"q": "home assistant", "count": "1"}

    try:
        async with asyncio.timeout(REQUEST_TIMEOUT_SECONDS):
            response = await session.get(
                BRAVE_SEARCH_URL, headers=headers, params=params
            )
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        raise CannotConnect from error

    if response.status in (401, 403):
        raise InvalidAuth
    if response.status != 200:
        raise CannotConnect


class BraveSearchConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the Brave Search integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """
        Handle the single step where the user enters the Brave Search API key.

        param user_input: The form data submitted by the user, or None on first display.

        :return: The config flow result: the created entry, or the form again with errors.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await _async_validate_api_key(self.hass, user_input[CONF_API_KEY])
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Brave Search", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
