## Project Overview
A FastAPI webhook service for UK trades businesses (plumbers, electricians 
etc). Core features:
1. Missed-call auto text-back: when a call to the Twilio number goes 
   unanswered, automatically SMS the caller back within seconds.
2. Booking form (/book): a shareable mobile page where customers submit 
   their details; the owner is texted instantly and the booking is logged.
3. Owner dashboard (/dashboard): password-protected page listing new 
   bookings, missed calls, and scheduled reviews.
4. Approval-driven review requests: the owner approves a finished job on 
   the dashboard, and the customer gets a review-request SMS the next day 
   at REVIEW_SEND_HOUR (UTC). The legacy /job-complete API still works.

## Tech Stack
- Python 3.11
- FastAPI + uvicorn
- Twilio Python SDK (calls, SMS, TwiML)
- APScheduler (delayed review SMS)
- python-dotenv for env vars
- Fly.io for hosting
- JSON file storage (missed_calls.json, review_requests.json, 
  bookings.json) — structured to be swappable for a DB later

## Project Structure
/
├── main.py              
├── config.py            
├── scheduler.py         
├── storage.py           
├── twilio_helpers.py    
├── templates.py         # server-rendered HTML (no template engine)
├── requirements.txt
├── Dockerfile
├── fly.toml
├── .env.example
├── .gitignore
└── CLAUDE.md

## Environment Variables
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
BUSINESS_OWNER_NUMBER=
BUSINESS_CALLBACK_LINK=
BUSINESS_REVIEW_LINK=
BUSINESS_NAME=
BUSINESS_TAGLINE=
DASHBOARD_PASSWORD=
REVIEW_SEND_HOUR=        # hour (UTC) the next-day review SMS is sent; default 10

## Endpoints
POST /voice         → TwiML: ring 20s, redirect to /missed-call if no answer
POST /missed-call   → send SMS to caller, log to missed_calls.json
GET  /book          → mobile booking form for customers
POST /book          → log booking, text details to owner
GET  /dashboard     → owner dashboard (HTTP Basic, password = DASHBOARD_PASSWORD)
POST /approve       → approve a booking, schedule next-day review SMS (auth)
POST /job-complete  → legacy API: schedules a next-day review SMS
GET  /logs          → returns missed_calls.json (for demo purposes)

## Config Design
All business-specific values (message templates, links, ring duration) 
live in config.py so this can be customized per client later.

## Key Constraints
- No database — JSON file storage only (MVP). Dashboard uses simple HTTP 
  Basic auth (password only); customer-facing pages are server-rendered HTML.
- Must work end-to-end locally via ngrok before deploying to Fly.io
- README must include: local setup, ngrok testing, Fly.io deploy steps
- .env must never be committed

## Gotchas — read before changing review/scheduling code
- Scheduled reviews live in-memory (APScheduler), so they do NOT survive a 
  restart on their own. `scheduler.reschedule_pending_reviews()` runs on 
  startup and re-adds jobs from APPROVED bookings in bookings.json. 
  IMPORTANT GAP: reviews scheduled via the legacy `/job-complete` path are 
  only logged to review_requests.json (no booking record) and are NOT 
  re-hydrated — a restart loses them. Prefer the dashboard approve flow.
- JSON storage is ephemeral on Fly.io: the container filesystem resets on 
  every redeploy, so bookings.json / missed_calls.json / review_requests.json 
  are wiped. Fine for a demo; needs a Fly volume or DB for production.
- REVIEW_SEND_HOUR is interpreted as UTC. The UK runs UTC+1 during BST 
  (late Mar–late Oct), so e.g. 10 sends at 11:00 UK time in summer. Make it 
  timezone-aware if exact local time matters.
- Dashboard auth fails closed: an empty DASHBOARD_PASSWORD denies all 
  /dashboard and /approve access. It is password-only HTTP Basic (any 
  username) — single-owner grade, not multi-user/role-based.
- templates.py renders raw HTML; always html.escape() any customer-supplied 
  value (name/address/details) before interpolating, or you reintroduce XSS 
  on the dashboard.

## Possible Next Steps
- Persist data in a real store (SQLite + Fly volume, or Postgres) so 
  bookings/reviews survive redeploys and restarts.
- Re-hydrate legacy /job-complete reviews too, or unify all review 
  scheduling behind booking records (single source of truth).
- Add dashboard actions: cancel a scheduled review, or mark a job "not done".
- Timezone-aware review send time (handle BST).
- Owner notifications beyond SMS (email / WhatsApp) on new bookings.
