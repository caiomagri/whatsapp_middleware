import os
import io
import requests
import logging

from twilio.rest import Client
from faster_whisper import WhisperModel
from twilio.twiml.messaging_response import MessagingResponse

from app.utils.chatbot import Chatbot
from app.models.webhook import WebhookPayload

_logger = logging.getLogger(__name__)

DEFAULT_ERROR_MSG = "Foi mal, não entendi. Pode repetir?"


class WebhookResponse:
    AUDIO = "audio/ogg"

    @staticmethod
    async def send_message(body: str, to: str):
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        whatsapp_number = os.environ["TWILIO_WHATSAPP_NUMBER"]
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=f"whatsapp:{whatsapp_number}",
            body=body,
            to=to,
        )

        return message

    @staticmethod
    def make_response_from_bot_answer(text: str):
        bot_response = Chatbot.call(text)
        data = bot_response.json()
        answer = data["answer"]
        return answer

    @staticmethod
    def transcribe(media_url: str, model):
        if os.getenv("AUDIO_TRANSCRIBE_MODEL") == "whisper":
            segments, _ = model.transcribe(
                media_url,
                language="pt",
                beam_size=5,
            )
            text = " ".join([segment.text for segment in segments])
        else:
            import uuid
            from pydub import AudioSegment

            audio_response = requests.get(media_url)
            audio_content = audio_response.content
            audio_buffer = io.BytesIO(audio_content)
            audio_segment = AudioSegment.from_file(audio_buffer)
            audio_id = str(uuid.uuid4())
            ogg_path = f"/app/data/temp/{audio_id}_temp_audio.ogg"
            audio_segment.export(ogg_path, format="ogg")
            response = model.transcribe([ogg_path])
            text = response[0].get("transcription")
            os.remove(ogg_path)
        return text

    @staticmethod
    def process_webhook_text(
        payload: WebhookPayload,
    ) -> None:
        _logger.warning(f"process_webhook_text Received form: {payload}")

        try:
            message = WebhookResponse.make_response_from_bot_answer(
                payload.Body,
            )
        except Exception as e:
            _logger.error(f"Error processing process_webhook_text: {e}")
            message = DEFAULT_ERROR_MSG

        response = MessagingResponse()
        response.message(message)
        return response

    @staticmethod
    async def process_webhook_voice(
        whisper_model: WhisperModel,
        payload: WebhookPayload,
    ) -> None:
        _logger.warning(f"process_webhook Received form: {payload}")

        try:
            if (
                payload.NumMedia > 0
                and payload.MediaContentType0 == WebhookResponse.AUDIO
            ):
                text = WebhookResponse.transcribe(
                    payload.MediaUrl0,
                    whisper_model,
                )
                _logger.warning(f"Whisper: {text}")
                message = WebhookResponse.make_response_from_bot_answer(text)
            else:
                message = "Infelizmente não consigo processar esse tipo de mensagem, tente enviar um áudio ou texto."
        except Exception as e:
            _logger.error(f"Error processing process_webhook_voice: {e}")
            message = DEFAULT_ERROR_MSG

        await WebhookResponse.send_message(message, payload.From)

    def call_chatbot(self, text: str):
        return self.chatbot.get_response(text)
