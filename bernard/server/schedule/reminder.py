from typing import Union, Literal
from pydantic import BaseModel
import datetime as dt

from ...session import SessionContext
from .event import BaseScheduleEvent


class BaseReminder(BaseModel):
    # relative_event: BaseScheduleEvent
    remind_content: str
    remind_date: Union[dt.date, Literal['unknown']]
    remind_time: Union[dt.time, Literal['unknown']]

    def unknown_fields(self):
        ret = []
        for i in self:
            if i[1] == 'unknown':
                ret.append(i[0])
        return ret
    
    @classmethod
    def create_on_event(cls, event:BaseScheduleEvent):
        return cls(
            relative_event=event,
            remind_date='unknown',
            remind_time='unknown'
        )
