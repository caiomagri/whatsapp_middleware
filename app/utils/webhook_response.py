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
    def send_message(body: str, to: str):
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
        _logger.warning(f"WebhookResponse Bot Answer: {answer}")
        return answer

    @staticmethod
    def process_webhook(
        whisper_model: whisper.Whisper,
        payload: WebhookPayload,
    ) -> MessagingResponse:
        _logger.warning(f"process_webhook Received form: {payload}")

        response = MessagingResponse()

        try:
            if payload.Body:
                response.message(
                    WebhookResponse.make_reponse_from_bot_answer(payload.Body)
                )
            elif (
                payload.NumMedia > 0
                and payload.MediaContentType0 == WebhookResponse.AUDIO
            ):
                stt = whisper_model.transcribe(
                    payload.MediaUrl0,
                    language="pt",
                    fp16=False,
                    verbose=True,
                    patience=2,
                    beam_size=5,
                )
                text = stt["text"]

                _logger.warning(f"Whisper: {stt}")
                answer = WebhookResponse.make_reponse_from_bot_answer(text)
                response.message(answer)
            else:
                response.message("Não sei o que fazer com isso")
        except Exception as e:
            _logger.error(f"Error processing webhook: {e}")
            response.message("Tipo, deu ruim aqui")

        return response

    def call_chatbot(self, text: str):
        return self.chatbot.get_response(text)
