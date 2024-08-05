
import dspy
from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from typing import Annotated, NamedTuple, Literal, Optional, Union

from .dialogue import Dialogue
from .llm import SessionEndSig

class SessionContext(BaseModel):
    dialogue: Dialogue


class SessionEndDiscriminator:

    def __init__(self):
        self.session_end_discriminator = dspy.TypedPredictor(SessionEndSig)
    
    def is_session_ended(self, dialogue: Dialogue) -> bool:
        return self.session_end_discriminator(dialogue=dialogue).is_session_ended
    
    