## Project Overview
A FastAPI webhook service for UK trades businesses (plumbers, electricians 
etc). Two core features:
1. Missed-call auto text-back: when a call to the Twilio number goes 
   unanswered, automatically SMS the caller back within seconds.
2. Review request automation: owner triggers a "job complete" event, 
   system sends the customer an SMS review request 2 hours later.

## Tech Stack
- Python 3.11
- FastAPI + uvicorn
- Twilio Python SDK (calls, SMS, TwiML)
- APScheduler (delayed review SMS)
- python-dotenv for env vars
- Fly.io for hosting
- JSON file storage (missed_calls.json, review_requests.json) — 
  structured to be swappable for a DB later

## Project Structure
/
├── main.py              
├── config.py            
├── scheduler.py         
├── storage.py           
├── twilio_helpers.py    
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
BUSINESS_CALLBACK_LINK=
BUSINESS_REVIEW_LINK=

## Endpoints
POST /voice         → TwiML: ring 20s, redirect to /missed-call if no answer
POST /missed-call   → send SMS to caller, log to missed_calls.json
POST /job-complete  → accepts customer number, schedules review SMS 2hrs later
GET  /logs          → returns missed_calls.json (for demo purposes)

## Config Design
All business-specific values (message templates, links, ring duration) 
live in config.py so this can be customized per client later.

## Key Constraints
- No auth, no database, no frontend needed yet — MVP only
- Must work end-to-end locally via ngrok before deploying to Fly.io
- README must include: local setup, ngrok testing, Fly.io deploy steps
- .env must never be committed
