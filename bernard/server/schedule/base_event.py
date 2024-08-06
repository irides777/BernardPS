from typing import Union, Literal, Optional
from pydantic import BaseModel
import datetime as dt

from ...session import SessionContext


class BaseScheduleEvent(BaseModel):
    event_name: str
    event_content: str
    event_date: Union[dt.date, Literal['unknown']]
    event_time: Optional[Union[dt.time, Literal['unknown']]]

    def unknown_fields(self):
        ret = []
        for i in self:
            if i[1] == 'unknown' and i[0] != 'event_time':
                ret.append(i[0])
        return ret
    