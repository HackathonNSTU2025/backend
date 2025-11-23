from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class QueueEntryBase(BaseModel):
    user_id: int


class QueueEntryCreate(QueueEntryBase):
    station_id: int


class QueueEntry(QueueEntryBase):
    queue_id: int
    position: int
    joined_at: datetime
    served_at: Optional[datetime] = None
