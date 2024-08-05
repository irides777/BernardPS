
import logging
import dspy

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from .llm import ScheduleEventLLM, ScheduleEventConfirmSig


class ScheduleEventServer:
    def __init__(self, ui):
        self.name = 'Schedule Event'
        self.ui = ui
        self.event_creator = ScheduleEventLLM().activate_assertions(max_backtracks=1)
        self.event_confirmor = dspy.TypedPredictor(ScheduleEventConfirmSig)
        self.reply_confirm = dspy.TypedPredictor(ReplyInformationConfirmSig)
        self.reply_query = dspy.TypedPredictor(ReplyQuerySig)

    def add_event(self, event):
        print(f'Event added: {event}')
    
    async def process_dialogue(self, dialogue: Dialogue):
        logging.info(f'Dialogue: {dialogue}')
        event = self.event_creator(dialogue=dialogue)
        logging.info(f'Event created: {event}')
        unknown_fields = event.unknown_fields()
        if len(unknown_fields) == 0:
            reply_for_confirmation = self.reply_confirm(dialogue=dialogue, information_need_check=event).reply
            dialogue_after_confirm = await self.ui.send_wait_reply(reply_for_confirmation)
            # dialogue_after_confirm = await self.ui.send_wait_reply(f'Are you sure create {event}?')
            logging.info(f'Dialogue after confirm: {dialogue_after_confirm}')
            if self.event_confirmor(dialogue=dialogue_after_confirm).confirmation:
                logging.info(f'Event confirmed: {event}')
                self.add_event(event)
                self.ui.send_to_user('event created successfully!')
            else:
                logging.info(f'Event not confirmed: {event}')
                await self.ui.route(dialogue=dialogue_after_confirm)
        else:
            reply_for_more_information = self.reply_query(dialogue=dialogue, incomplete_data=event).reply
            self.ui.send_to_user(reply_for_more_information)
            # self.ui.send_to_user(f'{unknown_fields} are unknown, please provide relevant information.')