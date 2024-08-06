import dspy

from ...session import Dialogue
from .reminder import BaseReminder

class ReminderConstructorSig(dspy.Signature):
    """   
    You are user's assistant, please extract the detail of reminder user mentioned in dialogue, fill the relevant information to construct a reminder for storing into database. Notice: the time of reminder is different from schedule event. If user have not mentioned information about reminder, just fill it with 'unknown'.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder: BaseReminder = dspy.OutputField(desc="the reminder user want to set. If there is insuffient information to fill a field, just fill it with 'unknown'.")


class ReminderCheckerSig(dspy.Signature):
    """ 
    Verify that the auto generated reminder is based on the event user mentioned in provided dialogue. Especially check the datetime and weekday.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder: BaseReminder = dspy.InputField(desc="the reminder user mentioned")
    faithfulness: bool = dspy.OutputField(desc="Only output True or False indicating if reminder is faithful to dialogue, other redundant information should be ignored. Notice that reminder is different from schedule event.")



class ReminderLLM(dspy.Module):

    def __init__(self):
        super().__init__()
        self.reminder_constructor = dspy.TypedChainOfThought(ReminderConstructorSig)
        self.reminder_checker = dspy.TypedPredictor(ReminderCheckerSig)
    
    def forward(self, dialogue: Dialogue):
        reminder = self.reminder_constructor(dialogue=dialogue).reminder
        dspy.Suggest(
            self.reminder_checker(dialogue=dialogue, reminder=reminder).faithfulness,
            f"Reminder created {reminder} is not consistent with user mentioned in dialogue"
        )
        return reminder