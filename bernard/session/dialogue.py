from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from typing import Annotated, NamedTuple, Literal, Optional, Union
import datetime as dt

class Message(BaseModel):
    role: Literal['User', 'Assistant']
    content: str
    date: Optional[dt.date] = None
    time: Optional[dt.time] = None
    weekday: Optional[Literal['Mon','Tue','Wed','Thu','Fri','Sat','Sun']]
    
Dialogue = RootModel[list[Message]]