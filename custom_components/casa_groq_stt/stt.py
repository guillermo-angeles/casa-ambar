import logging

from homeassistant.components import stt

from .client import DOMAIN, GroqAuthError, GroqError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([GroqSpeechEntity(entry)])


class GroqSpeechEntity(stt.SpeechToTextEntity):
    _attr_name = "Casa Groq STT"

    def __init__(self, entry):
        self._entry = entry
        self._attr_unique_id = DOMAIN

    @property
    def supported_languages(self):
        return ["es"]

    @property
    def supported_formats(self):
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self):
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self):
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self):
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self):
        return [stt.AudioChannels.CHANNEL_MONO]

    @property
    def audio_processing(self):
        return stt.SpeechAudioProcessing(
            requires_external_vad=True,
            prefers_auto_gain_enabled=True,
            prefers_noise_reduction_enabled=True,
        )

    async def async_process_audio_stream(self, metadata, stream):
        if not self.check_metadata(metadata):
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
        try:
            text = await self._entry.runtime_data.transcribe(stream)
        except GroqAuthError:
            self._entry.async_start_reauth(self.hass)
            _LOGGER.warning("Groq requiere renovar la clave en la interfaz")
        except GroqError as err:
            _LOGGER.warning("Transcripción Groq no disponible: %s", err)
        else:
            return stt.SpeechResult(text, stt.SpeechResultState.SUCCESS)
        return stt.SpeechResult(None, stt.SpeechResultState.ERROR)
