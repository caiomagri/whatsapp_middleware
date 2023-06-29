import os
import logging

import whisper
from twilio.rest import Client
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
    def process_webhook_text(
        payload: WebhookPayload,
    ) -> None:
        _logger.warning(f"process_webhook_text Received form: {payload}")

        try:
            message = WebhookResponse.make_reponse_from_bot_answer(
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
        whisper_model: whisper.Whisper,
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
                message = WebhookResponse.make_reponse_from_bot_answer(text)
            else:
                message = "Infelizmente não consigo processar esse tipo de mensagem, tente enviar um áudio ou texto."
        except Exception as e:
            _logger.error(f"Error processing process_webhook_voice: {e}")
            message = DEFAULT_ERROR_MSG

        await WebhookResponse.send_message(message, payload.From)

    def call_chatbot(self, text: str):
        return self.chatbot.get_response(text)
