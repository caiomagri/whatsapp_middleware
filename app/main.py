import os
import whisper
from twilio.request_validator import RequestValidator
from fastapi import FastAPI, Response, Request, HTTPException

from app.models.webhook import WebhookPayload
from app.utils.webhook_response import WebhookResponse

app = FastAPI()
whisper_model = whisper.load_model(os.getenv("WHISPER_LOAD_MODEL"))


@app.get("/health_check")
def health_check():
    return {"message": "alive"}


@app.post("/webhook")
async def chat(
    request: Request,
):
    form_ = await request.form()
    # validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    # if not validator.validate(
    #     str(request.url),
    #     form_,
    #     request.headers.get("X-Twilio-Signature", "")
    # ):
    #     raise HTTPException(status_code=400, detail="Error in Twilio Signature")

    webhook_payload = WebhookPayload(**form_)
    response = WebhookResponse.process_webhook(whisper_model, webhook_payload)

    return Response(content=str(response), media_type="application/xml")
