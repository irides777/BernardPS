
import logging
from typing import Optional
import dspy
import re
import datetime as dt
from typing import Union, Literal

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from ..request import RequestServer
from .reminder import BaseReminder
from .datetime import relative_date_cal, process_raw_date


class ReminderContentConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is setting a reminder, please extract the detail of reminder content user mentioned in dialogue. The return should be the same language as user's input. 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder_content: str = dspy.OutputField(desc="The remind content user want to set, be brief and clear, do not add any explanation or title. If user doesn't mention specific content, just fill it with 'reminder'.")

class ReminderDateConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is setting a reminder, please extract the date (time is not required) of reminder user mentioned in dialogue. The return should be the same language as user's input (except 'unknown'). 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder_date: Union[dt.date, str] = dspy.OutputField(desc="The reminder date user want to set. Notice: if the date user mentioned is weekday related (e.g. next Wed, 这周五), you don't need to transform relative date into absolute date, just return exactly what user said. Otherwise, If user mentioned absolute date, return the date in format 'YYYY-MM-DD', with the current date information mentioned in dialogue. If there is insuffcient information to fill a field, just fill it with 'unknown'. DO NOT ADD ANY EXPLANATION.")


class ReminderTimeConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is setting a reminder, please extract the time (date is not needed) of reminder user mentioned in dialogue.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder_time: Union[dt.time, Literal['unknown']] = dspy.OutputField(desc="The reminder time user want to set, not include date. (e.g. 10:00, 14:00, 17:30, etc.) If user doesn't mention specific time, just fill it with 'unknown'. ANY OUTPUT OTHER THAN 'unknown' DO NOT ADD ANY EXPLANATION.")

class ReminderCheckerSig(dspy.Signature):
    """ 
    Verify that the auto generated reminder is based on the event user mentioned in provided dialogue. Especially check the datetime and weekday.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reminder: BaseReminder = dspy.InputField(desc="the reminder user mentioned")
    faithfulness: bool = dspy.OutputField(desc="ONLY output True or False indicating if reminder is faithful to dialogue, other redundant information should be ignored. Notice that reminder is different from schedule event.")



class ReminderLLM(dspy.Module):

    def __init__(self):
        super().__init__()
        self.reminder_content_constructor = dspy.TypedPredictor(ReminderContentConstructorSig, max_retries=3)
        self.reminder_date_constructor = dspy.TypedPredictor(ReminderDateConstructorSig)
        self.reminder_time_constructor = dspy.TypedPredictor(ReminderTimeConstructorSig)
        self.reminder_checker = dspy.TypedPredictor(ReminderCheckerSig)
    
    def forward(self, dialogue: Dialogue):
        # reminder_reply = self.reminder_constructor(dialogue=dialogue)
        # print(reminder_reply)
        raw_reminder_content = self.reminder_content_constructor(dialogue=dialogue).reminder_content
        reminder_content = raw_reminder_content.split('\n')[0]
        # print(reminder_content)

        raw_reminder_date = self.reminder_date_constructor(dialogue=dialogue).reminder_date
        # print(raw_reminder_date)

        reminder_date = process_raw_date(dialogue=dialogue, raw_date=raw_reminder_date)

        reminder_time = self.reminder_time_constructor(dialogue=dialogue).reminder_time
        # print(reminder_time)
        # reminder_time = raw_reminder_time if raw_reminder_time != 'unknown' else '12:00'

        # print(f"reminder_date: {reminder_date}, reminder_time: {reminder_time}")
        reminder = BaseReminder(remind_content=reminder_content, remind_date=reminder_date, remind_time=reminder_time)


        return reminder

class ReminderServer(RequestServer):
    
    def __init__(self, channel):
        name = 'Create Time Reminder'
        super().__init__(name=name, channel=channel, RequestLLM=ReminderLLM)

    def add_request(self, reminder: BaseReminder):
        print(f'Reminder added: {reminder}')
        self.channel.reminders.append(reminder)