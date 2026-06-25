# missed-call-textback

FastAPI webhook service for UK trades businesses. Features:
1. **Missed-call auto text-back** — when a call to your Twilio number goes unanswered, the caller gets an SMS within seconds.
2. **Booking form** — a shareable mobile page (`/book`) where customers submit their details; the owner is texted instantly.
3. **Owner dashboard** — a password-protected page (`/dashboard`) listing new bookings, missed calls, and scheduled reviews.
4. **Approval-driven review requests** — the owner approves a finished job on the dashboard, and the customer gets a review-request SMS the **next day** at a sensible hour (no more blind fixed delay).

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
BUSINESS_REVIEW_LINK=https://g.page/r/your-review-link
BUSINESS_NAME=Dave's Plumbing
BUSINESS_TAGLINE=Fast, reliable, local plumber in Manchester
DASHBOARD_PASSWORD=change-me
REVIEW_SEND_HOUR=10
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

### 4. Test the booking → approval → review flow

1. Open `http://localhost:8000/book`, fill in the form, and submit. The owner number receives an SMS and the booking lands in `bookings.json`.
2. Open `http://localhost:8000/dashboard` (any username, password = `DASHBOARD_PASSWORD`). The booking appears under **New bookings**.
3. Click **✓ Approve & request review**. The booking moves to **Reviews scheduled** with a send time of tomorrow at `REVIEW_SEND_HOUR` (UTC).

To verify the review SMS actually sends, temporarily set `REVIEW_SEND_HOUR` to the current hour and approve a booking close to that time. The legacy `POST /job-complete` API still works and schedules a next-day review too:

```bash
curl -X POST http://localhost:8000/job-complete \
  -d "customer_number=+447700900000&customer_name=John"
```

### 5. View logs

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
  BUSINESS_CALLBACK_LINK=https://... \
  BUSINESS_REVIEW_LINK=https://... \
  BUSINESS_NAME="Dave's Plumbing" \
  BUSINESS_TAGLINE="Fast, reliable, local" \
  DASHBOARD_PASSWORD=a-strong-password \
  REVIEW_SEND_HOUR=10
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
| GET | `/book` | Mobile booking form for customers |
| POST | `/book` | Logs the booking and texts details to the owner |
| GET | `/dashboard` | Owner dashboard (HTTP Basic auth, password = `DASHBOARD_PASSWORD`) |
| POST | `/approve` | Approves a booking and schedules its next-day review SMS (auth) |
| POST | `/job-complete` | Legacy API — schedules a next-day review SMS (`customer_number`, `customer_name` form fields) |
| GET | `/logs` | Returns all missed call records |
