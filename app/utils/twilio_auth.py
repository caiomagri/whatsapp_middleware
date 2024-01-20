import re
import os
import hmac
import base64
import hashlib

from fastapi import HTTPException


def twilio_auth(request, form_=None):
    twilio_signature = request.headers.get('X-Twilio-Signature', None)

    if not twilio_signature:
        raise HTTPException(status_code=403, detail="Forbidden")

    domain = re.sub('http', 'https', str(request.url))

    if form_:
        for k, v in sorted(form_.items()):
            domain += k + v

    mac = hmac.new(
        bytes(os.environ["TWILIO_AUTH_TOKEN"], 'UTF-8'),
        domain.encode("utf-8"),
        hashlib.sha1
    )

    computed = base64.b64encode(mac.digest())
    computed = computed.decode('utf-8')
    diy_signature = computed.strip()

    if diy_signature != twilio_signature:
        raise HTTPException(status_code=403, detail="Forbidden")
