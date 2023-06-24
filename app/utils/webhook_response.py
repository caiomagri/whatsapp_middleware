import os
import logging

import whisper
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app.models.webhook import WebhookPayload

_logger = logging.getLogger(__name__)


class WebhookResponse:
    AUDIO = "audio/ogg"
    
    @staticmethod
    def send_message(body: str, to: str):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        whatsapp_number = os.environ['TWILIO_WHATSAPP_NUMBER']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=f'whatsapp:{whatsapp_number}',
            body=body,
            to=to,
        )

        return message

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
                    f"Oi {payload.ProfileName}, você escreveu isso: {payload.Body}" # noqa
                )
            elif (
                payload.NumMedia > 0
                and payload.MediaContentType0 == WebhookResponse.AUDIO
            ):
                WebhookResponse.send_message(
                    f"Só 1 segundo, estou ouvindo seu audio...", # noqa
                    to=payload.From,
                )
                stt = whisper_model.transcribe(
                    payload.MediaUrl0,
                    language="pt",
                    fp16=False,
                    verbose=True,
                    patience=2,
                    beam_size=5,
                )

                _logger.warning(f"Whisper: {stt}")
                response = MessagingResponse()
                response.message(
                    f"Oi {payload.ProfileName}, traduzi seu audio: {stt['text']}" # noqa
                )
            else:
                response.message("Não sei o que fazer com isso")
        except Exception as e:
            _logger.error(f"Error processing webhook: {e}")
            response.message("Tipo, deu ruim aqui")

        return response
