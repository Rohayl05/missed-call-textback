import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_PHONE_NUMBER = os.environ["TWILIO_PHONE_NUMBER"]
BUSINESS_OWNER_NUMBER = os.environ["BUSINESS_OWNER_NUMBER"]
BUSINESS_CALLBACK_LINK = os.environ.get("BUSINESS_CALLBACK_LINK", "")

# Twilio call behaviour
RING_DURATION_SECONDS = 20

# SMS templates — edit per client
MISSED_CALL_MESSAGE = (
    "Hi, sorry we missed your call! We'll get back to you as soon as possible. "
    "In the meantime, you can book a callback here: {callback_link}"
)
