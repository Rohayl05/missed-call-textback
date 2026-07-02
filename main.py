from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
import config
import storage
import twilio_helpers

app = FastAPI()


@app.post("/voice")
async def voice(request: Request):
    """Return TwiML that rings for RING_DURATION_SECONDS then hits /missed-call."""
    base_url = str(request.base_url).rstrip("/")
    missed_call_url = f"{base_url}/missed-call"
    twiml = twilio_helpers.build_voice_twiml(missed_call_url)
    return Response(content=twiml, media_type="application/xml")


@app.post("/missed-call")
async def missed_call(
    From: str = Form(...),
    DialCallStatus: str = Form(default="no-answer"),
):
    """Triggered by Twilio when a call goes unanswered. Sends an SMS and logs the call."""
    if DialCallStatus != "completed":
        body = config.MISSED_CALL_MESSAGE.format(
            callback_link=config.BUSINESS_CALLBACK_LINK
        )
        twilio_helpers.send_sms(to=From, body=body)
        storage.log_missed_call(caller=From)
    return Response(content="<Response/>", media_type="application/xml")


@app.get("/logs")
async def logs():
    """Return all missed call records (demo endpoint)."""
    return storage.get_missed_calls()
