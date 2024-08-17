from typing import Union, Literal
from pydantic import BaseModel, model_validator, Field
import datetime as dt

from ...session import SessionContext

WEEKDAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
LLMDate = Union[dt.date, Literal['unknown']]
LLMTime = Union[dt.time, Literal['unknown']]

class BaseTask(BaseModel):
    task_content: str
    deadline_date: LLMDate
    first_step: str
    next_remind_date: LLMDate
    next_remind_time: LLMTime
    next_remind_weekday: Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] = Field(default=None)


    @model_validator(mode='after')
    def set_remind_weekday(cls, values):
        date = values.next_remind_date
        if date == 'unknown':
            values.next_remind_weekday = 'unknown'
        else:
            values.next_remind_weekday = WEEKDAYS[date.weekday()]
        return values

    def unknown_fields(self):
        ret = []
        for i in self:
            if i[1] == 'unknown':
                ret.append(i[0])
        return ret

class BaseProgress(BaseModel):
    task_current_progress: str
    last_step_finished: bool
    progress_update_date: LLMDate
    next_step: str
    next_remind_date: LLMDate
    next_remind_time: LLMTime

class Task(BaseModel):
    basetask: BaseTask
    progresses: list[BaseProgress]
    next_remind_date: dt.date
    next_remind_time: dt.time


    