
import logging
from typing import Optional
import dspy

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from .reminder_llm import ReminderConstructorSig, ReminderCheckerSig, ReminderLLM
from .reminder import BaseReminder
from .base_event import BaseScheduleEvent
from .event import ScheduleEvent


class ReminderServer:
    def __init__(self, channel):
        self.name = 'Create Time Reminder'
        self.channel = channel
        self.reminder_creator = ReminderLLM().activate_assertions(max_backtracks=1)
        self.reply_confirm = dspy.TypedPredictor(ReplyInformationConfirmSig)
        self.reply_query = dspy.TypedPredictor(ReplyQuerySig)

    def add_reminder(self, reminder: BaseReminder):
        print(f'Reminder added: {reminder}')
    
    async def process_dialogue(self, dialogue: Dialogue):
        reminder = self.reminder_creator(dialogue=dialogue)
        unknown_fields = reminder.unknown_fields()
        if len(unknown_fields) == 0:
            reply_for_confirmation = self.reply_confirm(dialogue=dialogue, information_need_check=reminder).reply
            dialogue_after_confirm, confirm = await self.channel.send_wait_confirm(reply_for_confirmation)
            if confirm:
                self.add_reminder(reminder=reminder)
                self.channel.send_to_user('reminder created successfully!')
            else:
                await self.channel.route(dialogue=dialogue_after_confirm)
        else:
            reply_for_more_information = self.reply_query(dialogue=dialogue, incomplete_data=reminder).reply
            self.channel.send_to_user(reply_for_more_information)
