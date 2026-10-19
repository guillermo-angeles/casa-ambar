from pathlib import Path

from homeassistant.components import demo
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities([EchoCamera()])


class EchoCamera(Camera):
    _attr_name = "Echo Salón camera"
    _attr_unique_id = "stub_echo_salon_camera"

    async def async_camera_image(self, width=None, height=None):
        image = Path(demo.__file__).with_name("demo_1.jpg")
        return await self.hass.async_add_executor_job(image.read_bytes)
