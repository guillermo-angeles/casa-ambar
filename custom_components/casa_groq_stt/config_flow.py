import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .client import DOMAIN, GroqAuthError, GroqClient, GroqError

SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))})


class GroqConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _validate(self, user_input):
        client = GroqClient(async_get_clientsession(self.hass), user_input[CONF_API_KEY].strip())
        await client.validate()
        return {CONF_API_KEY: user_input[CONF_API_KEY].strip()}

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return await self._form("user", user_input)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._form("reauth_confirm", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)

    async def _form(self, step_id, user_input):
        errors = {}
        if user_input is not None:
            try:
                data = await self._validate(user_input)
            except GroqAuthError:
                errors["base"] = "invalid_auth"
            except GroqError:
                errors["base"] = "cannot_connect"
            else:
                if step_id == "reauth_confirm":
                    return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=data)
                if step_id == "reconfigure":
                    return self.async_update_reload_and_abort(self._get_reconfigure_entry(), data_updates=data)
                return self.async_create_entry(title="Casa Groq STT", data=data)
        return self.async_show_form(step_id=step_id, data_schema=SCHEMA, errors=errors)
