import re

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
import config


_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


def to_e164(raw: str, default_cc: str = "44") -> str:
    """Best-effort normalize a UK-entered phone number to E.164 for Twilio.

    Customers type local format ("07700 900123", "07700-900123") which Twilio
    cannot deliver to. Convert a leading national "0" to the country code and
    strip spacing. Numbers already in "+..." form are left untouched.
    """
    s = re.sub(r"[\s\-().]", "", raw or "")
    if s.startswith("+"):
        return s
    if s.startswith("00"):           # international access prefix -> "+"
        return "+" + s[2:]
    if s.startswith("0"):            # UK national: 07700... -> +447700...
        return "+" + default_cc + s[1:]
    if s.startswith(default_cc):     # already 447700... without the "+"
        return "+" + s
    return "+" + s                   # last resort: assume it's already international


def send_sms(to: str, body: str) -> str:
    """Send an SMS and return the message SID."""
    message = _client.messages.create(
        to=to,
        from_=config.TWILIO_PHONE_NUMBER,
        body=body,
    )
    return message.sid


def build_voice_twiml(missed_call_url: str) -> str:
    """
    Ring for RING_DURATION_SECONDS then redirect to missed_call_url if unanswered.
    Twilio calls the action URL when the <Dial> verb ends without the call being answered.
    """
    response = VoiceResponse()
    dial = Dial(
        action=missed_call_url,
        timeout=config.RING_DURATION_SECONDS,
    )
    dial.number(config.BUSINESS_OWNER_NUMBER)
    response.append(dial)
    return str(response)
