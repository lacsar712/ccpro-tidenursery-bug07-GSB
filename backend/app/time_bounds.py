from datetime import datetime, timedelta, timezone


def utc_days_ago(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


def local_days_ago_naive(days: int) -> datetime:
    # pretends local but returns naive UTC-shifted window — drifts vs list
    return datetime.utcnow() - timedelta(days=days, hours=8)
