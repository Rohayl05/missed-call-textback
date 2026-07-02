# missed-call-textback

FastAPI webhook service for UK trades businesses. When a call to your
Twilio number goes unanswered, the caller gets an SMS within seconds.

This is one half of a two-service split. The booking form, owner
dashboard, and review-request flow live in the sibling **review-requests**
project/repo.

---

## Local Setup

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd missed-call-textback
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+441234567890
BUSINESS_OWNER_NUMBER=+447700900000
BUSINESS_CALLBACK_LINK=https://calendly.com/yourname
```

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

---

## Testing with ngrok

ngrok exposes your local server so Twilio can reach it.

### 1. Install ngrok and start a tunnel

```bash
ngrok http 8000
```

Copy the `https://xxxx.ngrok-free.app` forwarding URL.

### 2. Configure Twilio webhooks

In the [Twilio Console](https://console.twilio.com), go to your phone number settings:

- **A call comes in** → Webhook → `https://xxxx.ngrok-free.app/voice`

### 3. Test missed-call flow

Call your Twilio number from another phone and don't answer. After ~20 seconds you should receive an SMS on the calling number.

### 4. View logs

```bash
curl http://localhost:8000/logs
```

---

## Fly.io Deployment

### 1. Install flyctl and log in

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
fly auth login
```

### 2. Launch the app (first time only)

```bash
fly launch
```

When prompted, skip adding a database. This creates `fly.toml`.

### 3. Set secrets

```bash
fly secrets set \
  TWILIO_ACCOUNT_SID=ACxxx \
  TWILIO_AUTH_TOKEN=xxx \
  TWILIO_PHONE_NUMBER=+44xxx \
  BUSINESS_OWNER_NUMBER=+44xxx \
  BUSINESS_CALLBACK_LINK=https://...
```

### 4. Deploy

```bash
fly deploy
```

### 5. Update Twilio webhook

Set your Twilio phone number's incoming call webhook to:
```
https://<your-app>.fly.dev/voice
```

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/voice` | TwiML response — rings 20s, redirects to `/missed-call` if unanswered |
| POST | `/missed-call` | Sends SMS to caller, logs to `missed_calls.json` |
| GET | `/logs` | Returns all missed call records |
