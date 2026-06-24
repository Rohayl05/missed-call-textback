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


def schedule_review(customer_number: str, customer_name: str) -> str:
    """Schedule a review SMS for REVIEW_DELAY_SECONDS from now. Returns ISO run time."""
    run_at = datetime.now(timezone.utc) + timedelta(seconds=config.REVIEW_DELAY_SECONDS)
    scheduler.add_job(
        _send_review_sms,
        trigger="date",
        run_date=run_at,
        args=[customer_number, customer_name],
        misfire_grace_time=60,
    )
    storage.log_review_request(
        customer_number=customer_number,
        customer_name=customer_name,
        scheduled_at=run_at.isoformat(),
    )
    return run_at.isoformat()
