
from typing import Union, Literal, Optional
from pydantic import BaseModel
import datetime as dt

from ...session import SessionContext
from .base_event import BaseScheduleEvent
from .reminder import BaseReminder

eid_count = 0

class ScheduleEvent(BaseModel):
    eid: int
    base_event: BaseScheduleEvent
    # active_reminder: Optional[BaseReminder]
    session_history: list[SessionContext]

    # @classmethod
    # def from_event_reminder(cls, base_event:BaseScheduleEvent, reminder:BaseReminder):
    #     self.eid = eid_count 
    #     eid_count += 1
    #     self.base_event = base_event
    #     self.active_reminder = reminder
    #     self.session_history = []
