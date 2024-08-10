
import dspy
from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from typing import Annotated, Any, NamedTuple, Literal, Optional, Union
from typing_extensions import TypedDict

from .dialogue import Dialogue

class SessionContext(TypedDict):
    dialogue: Dialogue
    intent: Optional[str] = None

class SessionEndSig(dspy.Signature):
    """  
    You are user's assistant, please analysis dialogue, and judge if user want to end the current topic in previous dialogue. Both user want to talk about another topic, and want to end the chat, all indicate the end of session, return True. Otherwise (i.e. still talk about current topic) return False. 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time.")
    is_session_ended: bool = dspy.OutputField(desc="True/False indicating if current session is ended by user.")

class SessionEndDiscriminator:

    def __init__(self):
        self.session_end_discriminator = dspy.TypedPredictor(SessionEndSig)
    
    def is_session_ended(self, dialogue: Dialogue) -> bool:
        return self.session_end_discriminator(dialogue=dialogue).is_session_ended
    
    