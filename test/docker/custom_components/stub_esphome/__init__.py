import logging

_LOGGER = logging.getLogger(__name__)

SERVICES = [
    "echo_sal_n_dashboard_path",
    "echo_sal_n_dashboard_show",
    "echo_sal_n_dashboard_hide",
    "echo_sal_n_home_show_camera",
]


async def async_setup(hass, config):
    def make(name):
        async def handler(call):
            _LOGGER.warning("STUB esphome.%s %s", name, dict(call.data))

        return handler

    for name in SERVICES:
        hass.services.async_register("esphome", name, make(name))
    return True
