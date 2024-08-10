from typing import Union, Literal
from pydantic import BaseModel, model_validator, Field
import datetime as dt

from ...session import SessionContext
from .event import BaseScheduleEvent

WEEKDAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

class BaseReminder(BaseModel):
    # relative_event: BaseScheduleEvent
    remind_content: str
    remind_date: Union[dt.date, Literal['unknown']]
    remind_time: Union[dt.time, Literal['unknown']]
    remind_weekday: Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] = Field(default=None)


    @model_validator(mode='after')
    def set_remind_weekday(cls, values):
        date = values.remind_date
        if date == 'unknown':
            values.remind_weekday = 'unknown'
        else:
            values.remind_weekday = WEEKDAYS[date.weekday()]
        return values

    
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
