from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    environment: str
    database: Literal["ok", "unavailable", "not_configured"]
    timestamp: datetime
