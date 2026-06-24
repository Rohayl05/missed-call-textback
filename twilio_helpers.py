from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
import config


_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


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
    # Dial the Twilio number itself so it rings — if nobody picks up within
    # timeout, Twilio hits the action URL with DialCallStatus != "completed".
    dial.number(config.TWILIO_PHONE_NUMBER)
    response.append(dial)
    return str(response)
