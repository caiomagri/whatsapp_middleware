import os
import logging

import whisper
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app.utils.chatbot import Chatbot
from app.models.webhook import WebhookPayload

_logger = logging.getLogger(__name__)


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
    def make_reponse_from_bot_answer(text: str):
        bot_reponse = Chatbot.call(text)
        data = bot_reponse.json()
        answer = data["answer"]
        return answer

    @staticmethod
    def transcribe(media_url: str, whisper_model: whisper.Whisper):
        segments, _ = whisper_model.transcribe(
            media_url,
            language="pt",
            beam_size=5,
        )
        text = " ".join([segment.text for segment in segments])
        return text

    @staticmethod
    async def process_webhook(
        whisper_model: whisper.Whisper,
        payload: WebhookPayload,
    ) -> None:
        _logger.warning(f"process_webhook Received form: {payload}")

        try:
            if payload.Body:
                message = WebhookResponse.make_reponse_from_bot_answer(
                    payload.Body,
                )
            elif (
                payload.NumMedia > 0
                and payload.MediaContentType0 == WebhookResponse.AUDIO
            ):
                text = WebhookResponse.transcribe(
                    payload.MediaUrl0,
                    whisper_model,
                )
                _logger.warning(f"Whisper: {text}")
                message = WebhookResponse.make_reponse_from_bot_answer(text)
            else:
                message = "Não sei o que fazer com isso"
        except Exception as e:
            _logger.error(f"Error processing webhook: {e}")
            message = "Tipo, deu ruim aqui"

        await WebhookResponse.send_message(message, payload.From)

    def call_chatbot(self, text: str):
        return self.chatbot.get_response(text)
