import os
import asyncio
from faster_whisper import WhisperModel

from fastapi import FastAPI, Response, Request

from app.models.webhook import WebhookPayload
from app.utils.webhook_response import WebhookResponse

app = FastAPI()

whisper_model = WhisperModel(
    os.getenv("WHISPER_LOAD_MODEL", "small"),
    device=os.getenv("WHISPER_DEVICE", "small"),
    compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
)


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
    asyncio.create_task(
        WebhookResponse.process_webhook(whisper_model, webhook_payload),
    )

    return Response(
        media_type="application/xml",
    )
