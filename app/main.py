import os
import asyncio

from fastapi import FastAPI, Response, Request

from app.models.webhook import WebhookPayload
from app.utils.webhook_response import WebhookResponse

app = FastAPI()

if os.getenv("AUDIO_TRANSCRIBE_MODEL") == "whisper":
    from faster_whisper import WhisperModel

    model = WhisperModel(
        os.getenv("WHISPER_LOAD_MODEL", "small"),
        device=os.getenv("WHISPER_DEVICE", "small"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )
else:
    import joblib
    model = joblib.load('./data/model/wav2wac_vhn.joblib')


@app.get("/health_check")
def health_check():
    return {"message": "alive"}


@app.post("/webhook")
async def chat(
    request: Request,
):
    form_ = await request.form()

    # TODO Autenticação com Twilio

    webhook_payload = WebhookPayload(**form_)

    if webhook_payload.Body:
        response = WebhookResponse.process_webhook_text(webhook_payload)
        return Response(
            content=str(response),
            media_type="application/xml",
        )

    asyncio.create_task(
        WebhookResponse.process_webhook_voice(model, webhook_payload),
    )

    return Response(
        media_type="application/xml",
    )
