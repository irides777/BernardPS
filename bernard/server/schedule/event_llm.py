import dspy

from ...session import Dialogue
from .event import BaseScheduleEvent

class ScheduleEventConstructorSig(dspy.Signature):
    """   
    Extract the schedule event user mentioned in dialogue, fill the relevant information to construct a event for storing into database.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    scheduled_event: BaseScheduleEvent = dspy.OutputField(desc="the event user mentioned. If there is insuffient information to fill a field, just fill it with 'unknown'.")


class ScheduleEventCheckerSig(dspy.Signature):
    """ 
    Verify that the auto generated scheudled event is based on the event user mentioned in provided dialogue. Especially check the datetime and weekday.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    scheduled_event: BaseScheduleEvent = dspy.InputField(desc="the event user mentioned")
    faithfulness: bool = dspy.OutputField(desc="Only output True or False indicating if scheduled event is faithful to dialogue, other redundant information should be ignored.")



class ScheduleEventLLM(dspy.Module):

    def __init__(self):
        super().__init__()
        self.event_constructor = dspy.TypedChainOfThought(ScheduleEventConstructorSig)
        self.event_checker = dspy.TypedPredictor(ScheduleEventCheckerSig)
    
    def forward(self, dialogue: Dialogue):
        event = self.event_constructor(dialogue=dialogue).scheduled_event
        dspy.Suggest(
            self.event_checker(dialogue=dialogue, scheduled_event=event).faithfulness,
            f"Event created {event} is not consistent with user mentioned in dialogue"
        )
        return event