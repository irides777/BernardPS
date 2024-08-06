
import logging
from typing import Optional
import dspy

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from .llm import ScheduleEventLLM, GeneralConfirmationSig
from .reminder import BaseReminder
from .base_event import BaseScheduleEvent
from .event import ScheduleEvent


class ReminderServer:
    def __init__(self, channel):
        self.name = 'Create Time Reminder'
        self.channel = channel
        self.event_creator = ScheduleEventLLM().activate_assertions(max_backtracks=1)
        self.event_confirmor = dspy.TypedPredictor(GeneralConfirmationSig)
        self.reply_confirm = dspy.TypedPredictor(ReplyInformationConfirmSig)
        self.reply_query = dspy.TypedPredictor(ReplyQuerySig)

    def add_reminder(self, reminder: BaseReminder):
        print(f'Reminder added: {reminder}')
    
    async def process_dialogue(self, dialogue: Dialogue):
        base_event = self.event_creator(dialogue=dialogue)
        unknown_fields = base_event.unknown_fields()
        if len(unknown_fields) == 0:
            reply_for_confirmation = self.reply_confirm(dialogue=dialogue, information_need_check=base_event).reply
            dialogue_after_confirm = await self.channel.send_wait_reply(reply_for_confirmation)
            if self.event_confirmor(dialogue=dialogue_after_confirm).confirmation:
                self.channel.router.direct_process(dialogue=dialogue, intent='Create Time Reminder')
                # if 'reminder' in self.channel.current_session:
                #     reminder = self.channel.current_session['reminder']:
                self.add_event(base_event=base_event)
                self.channel.send_to_user('event created successfully!')
            else:
                logging.info(f'Event not confirmed: {base_event}')
                await self.channel.route(dialogue=dialogue_after_confirm)
        else:
            reply_for_more_information = self.reply_query(dialogue=dialogue, incomplete_data=base_event).reply
            self.channel.send_to_user(reply_for_more_information)
            # self.ui.send_to_user(f'{unknown_fields} are unknown, please provide relevant information.')
