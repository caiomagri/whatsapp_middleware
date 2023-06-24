from pydantic import BaseModel


class WebhookPayload(BaseModel):
    AccountSid: str
    ApiVersion: str
    Body: str
    Forwarded: bool = None
    From: str
    MediaContentType0: str = None
    MediaUrl0: str = None
    MessageSid: str
    NumMedia: int
    NumSegments: int
    ProfileName: str
    ReferralNumMedia: int
    SmsMessageSid: str
    SmsSid: str
    SmsStatus: str
    To: str
    WaId: str
