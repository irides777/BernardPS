from pydantic import BaseModel
import datetime as dt

class BaseScheduleAction(BaseModel):
    name: str
    action_content: str
    act_date: dt.date
    act_time: dt.time

class ScheduleAction(BaseModel):
    aid: int
    eid: int
    action_detail: BaseScheduleAction