import secrets

from fastapi import FastAPI, Form, Request, Depends, HTTPException, status
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import config
import storage
import twilio_helpers
import scheduler as sched
import templates

app = FastAPI()
security = HTTPBasic()


def require_auth(creds: HTTPBasicCredentials = Depends(security)):
    """Password-only HTTP Basic auth for the owner dashboard (any username accepted)."""
    ok = bool(config.DASHBOARD_PASSWORD) and secrets.compare_digest(
        creds.password, config.DASHBOARD_PASSWORD
    )
    if not ok:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.on_event("startup")
def startup():
    sched.scheduler.start()
    sched.reschedule_pending_reviews()


@app.on_event("shutdown")
def shutdown():
    sched.scheduler.shutdown(wait=False)


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


@app.post("/job-complete")
async def job_complete(
    customer_number: str = Form(...),
    customer_name: str = Form(default="there"),
):
    """Schedule a review SMS to the customer for the next day (legacy API path)."""
    run_at = sched.schedule_review(
        customer_number=customer_number,
        customer_name=customer_name,
    )
    return {"status": "scheduled", "send_at": run_at, "customer": customer_number}


@app.get("/logs")
async def logs():
    """Return all missed call records (demo endpoint)."""
    return storage.get_missed_calls()


@app.get("/book", response_class=HTMLResponse)
async def book_form():
    """Mobile-first booking form for customers."""
    return HTMLResponse(content=templates.booking_form())


@app.post("/book", response_class=HTMLResponse)
async def book_submit(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(default=""),
    details: str = Form(default=""),
):
    """Log the booking and text the details to the owner."""
    storage.log_booking(name=name, phone=phone, address=address, details=details)
    twilio_helpers.send_sms(
        to=config.BUSINESS_OWNER_NUMBER,
        body=config.NEW_BOOKING_MESSAGE.format(
            name=name, phone=phone, address=address or "—", details=details or "—"
        ),
    )
    return HTMLResponse(content=templates.booking_confirmation())


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(_: None = Depends(require_auth)):
    """Owner dashboard: new bookings, scheduled reviews, and missed calls."""
    return HTMLResponse(
        content=templates.dashboard(
            bookings=storage.get_bookings(),
            missed_calls=storage.get_missed_calls(),
        )
    )


@app.post("/approve")
async def approve(
    booking_id: str = Form(...),
    _: None = Depends(require_auth),
):
    """Approve a finished job and schedule its review SMS for the next day."""
    booking = next(
        (b for b in storage.get_bookings() if b["id"] == booking_id and b["status"] == "new"),
        None,
    )
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found or already approved")
    run_at = sched.schedule_review(
        customer_number=booking["phone"],
        customer_name=booking["name"],
    )
    storage.approve_booking(booking_id, run_at)
    return RedirectResponse("/dashboard", status_code=303)
