## Project Overview
A FastAPI webhook service for UK trades businesses (plumbers, electricians
etc). Single feature: missed-call auto text-back — when a call to the
Twilio number goes unanswered, automatically SMS the caller back within
seconds.

This service used to also include a booking form, owner dashboard, and
approval-driven review requests. That functionality has been split out into
a separate sibling project, **review-requests**, which is a standalone
FastAPI service with its own repo, config, and deploy. If you're looking for
booking/dashboard/review code, it's over there.

## Tech Stack
- Python 3.11
- FastAPI + uvicorn
- Twilio Python SDK (calls, SMS, TwiML)
- python-dotenv for env vars
- Fly.io for hosting
- JSON file storage (missed_calls.json) — structured to be swappable for a
  DB later

## Project Structure
/
├── main.py
├── config.py
├── storage.py
├── twilio_helpers.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
└── CLAUDE.md

## Environment Variables
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
BUSINESS_OWNER_NUMBER=
BUSINESS_CALLBACK_LINK=

## Endpoints
POST /voice         → TwiML: ring 20s, redirect to /missed-call if no answer
POST /missed-call   → send SMS to caller, log to missed_calls.json
GET  /logs          → returns missed_calls.json (for demo purposes)

## Config Design
All business-specific values (message templates, links, ring duration)
live in config.py so this can be customized per client later.

## Key Constraints
- No database — JSON file storage only (MVP).
- Must work end-to-end locally via ngrok before deploying to Fly.io
- README must include: local setup, ngrok testing, Fly.io deploy steps
- .env must never be committed

## Gotchas
- JSON storage is ephemeral on Fly.io: the container filesystem resets on
  every redeploy, so missed_calls.json is wiped. Fine for a demo; needs a
  Fly volume or DB for production.

## Possible Next Steps
- Persist data in a real store (SQLite + Fly volume, or Postgres) so missed
  calls survive redeploys.
- Notify the owner (not just the caller) when a call is missed.
