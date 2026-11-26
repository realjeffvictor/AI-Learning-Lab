import math
import random
from datetime import timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import utcnow
from app.models import RateLimitHit

PRUNE_AFTER = timedelta(days=1)


def check(
    session: Session,
    bucket: str,
    key: str,
    limit: int,
    window_seconds: int,
    prune_probability: float = 0.01,
) -> None:
    """Count one request against (bucket, key). Raises a 429 with Retry-After when the window is already full.
    Under heavy concurrency the limit can be exceeded by a few requests; it is a brake, not an exact meter."""
    key = key[:80]
    now = utcnow()
    since = now - timedelta(seconds=window_seconds)
    count, oldest = session.execute(
        select(func.count(RateLimitHit.id), func.min(RateLimitHit.created_at)).where(
            RateLimitHit.bucket == bucket, RateLimitHit.key == key, RateLimitHit.created_at > since
        )
    ).one()
    if count >= limit:
        wait = max(1, math.ceil((oldest + timedelta(seconds=window_seconds) - now).total_seconds()))
        raise AppError(
            429, "rate_limited", "Too many requests. Please slow down and try again shortly.", {"Retry-After": str(wait)}
        )
    session.add(RateLimitHit(bucket=bucket, key=key, created_at=now))
    if random.random() < prune_probability:
        session.execute(delete(RateLimitHit).where(RateLimitHit.created_at < now - PRUNE_AFTER))
    session.commit()
