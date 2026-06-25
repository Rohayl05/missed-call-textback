from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import config
import twilio_helpers
import storage

scheduler = BackgroundScheduler(timezone="UTC")


def _send_review_sms(customer_number: str, customer_name: str) -> None:
    body = config.REVIEW_REQUEST_MESSAGE.format(
        name=customer_name,
        review_link=config.BUSINESS_REVIEW_LINK,
    )
    twilio_helpers.send_sms(to=customer_number, body=body)


def _next_day_send_time() -> datetime:
    """Tomorrow at REVIEW_SEND_HOUR (UTC)."""
    return (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=config.REVIEW_SEND_HOUR, minute=0, second=0, microsecond=0
    )


def schedule_review(customer_number: str, customer_name: str) -> str:
    """Schedule a review SMS for the next day at REVIEW_SEND_HOUR. Returns ISO run time."""
    run_at = _next_day_send_time()
    scheduler.add_job(
        _send_review_sms,
        trigger="date",
        run_date=run_at,
        args=[customer_number, customer_name],
        misfire_grace_time=3600,
    )
    storage.log_review_request(
        customer_number=customer_number,
        customer_name=customer_name,
        scheduled_at=run_at.isoformat(),
    )
    return run_at.isoformat()


def reschedule_pending_reviews() -> None:
    """On startup, re-add jobs for approved bookings whose review hasn't fired yet."""
    for b in storage.get_pending_reviews():
        scheduler.add_job(
            _send_review_sms,
            trigger="date",
            run_date=datetime.fromisoformat(b["review_scheduled_at"]),
            args=[b["phone"], b["name"]],
            misfire_grace_time=3600,
        )
