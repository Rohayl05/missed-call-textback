import json
import os
from datetime import datetime, timezone

MISSED_CALLS_FILE = "missed_calls.json"
REVIEW_REQUESTS_FILE = "review_requests.json"


def _read(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _write(path: str, data: list) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log_missed_call(caller: str, timestamp: str | None = None) -> None:
    records = _read(MISSED_CALLS_FILE)
    records.append({
        "caller": caller,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
    })
    _write(MISSED_CALLS_FILE, records)


def log_review_request(customer_number: str, customer_name: str, scheduled_at: str) -> None:
    records = _read(REVIEW_REQUESTS_FILE)
    records.append({
        "customer_number": customer_number,
        "customer_name": customer_name,
        "scheduled_at": scheduled_at,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    _write(REVIEW_REQUESTS_FILE, records)


def get_missed_calls() -> list:
    return _read(MISSED_CALLS_FILE)
