
import re
import dspy
from typing import Literal
import sys
import asyncio
import datetime as dt
from ..session import SessionContext, Dialogue, Message, SessionEndDiscriminator
from .channel_llm import GeneralConfirmationSig, LanguageTranslatorSig
from ..router import DialogueRouter

WEEKDAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

class Channel:
    def __init__(self, ui) -> None:
        self.workers = {}
        self.router = DialogueRouter(self)
        self.session_end_disc = SessionEndDiscriminator()
        self.confirmor = dspy.TypedPredictor(GeneralConfirmationSig)
        self.translator = dspy.TypedPredictor(LanguageTranslatorSig)
        self.current_session = None
        self.history_sessions = []
        self.reminders = []
        self.tasks = []
        self.step_map = {}
        self.ui = ui
    
    def _wrap_msg(self, msg, sender: Literal['User', 'Assistant']):
        # return Message.model_validate({'role': sender, 'content': msg, 'date': dt.datetime.now().date(), 'time': dt.datetime.now().time().replace(microsecond=0), 'weekday': WEEKDAYS[dt.datetime.now().weekday()]})
        return Message.model_validate({'role': sender, 'content': msg})

    def start_new_session(self, first_wrapped_msg: Message):
        print('new session started.')
        dialogue = Dialogue.model_validate({'root':[first_wrapped_msg], 'date': dt.datetime.now().date(), 'time': dt.datetime.now().time().replace(microsecond=0), 'weekday': WEEKDAYS[dt.datetime.now().weekday()]})
        self.current_session = SessionContext(dialogue=dialogue, intent=None)
    
    def end_current_session(self):
        self.history_sessions.append(self.current_session)
        self.current_session = None
        print('current session ended.')

    def _session_update(self, wrapped_msgs: list[Message]):
        self.current_session['dialogue'].root.extend(wrapped_msgs)

    def _hard_code_route(self, dialogue: Dialogue):
        latest_reply: Message = dialogue.root[-1]

        reminder_regex = re.compile(r"^(reminder[:：]|提醒[:：])", re.IGNORECASE)
        task_regex = re.compile(r"^(task[:：]|任务[:：])", re.IGNORECASE)
        progress_regex = re.compile(r"^(progress[:：]|进度[:：])", re.IGNORECASE)
        habit_regex = re.compile(r"^(habit[:：]|习惯[:：])", re.IGNORECASE)

        # print(latest_reply)
        # print(reminder_regex.match(latest_reply.content))

        if reminder_regex.match(latest_reply.content):
            return 'Create Time Reminder'
        elif task_regex.match(latest_reply.content):
            return 'Create Task'
        elif progress_regex.match(latest_reply.content):
            return 'Update Task Progress'
        elif habit_regex.match(latest_reply.content):
            return 'Create Habit'
        else:
            return None

    async def route(self):
        hard_code_intent = self._hard_code_route(self.current_session['dialogue'])
        if hard_code_intent and len(self.current_session['dialogue'].root) > 1:
            is_session_ended = True
        else:
            is_session_ended = self.session_end_disc.is_session_ended(self.current_session['dialogue'])

        if is_session_ended:
            last_msg = self.current_session['dialogue'].root[-1]
            self.end_current_session()
            self.start_new_session(first_wrapped_msg=last_msg)
        
        if hard_code_intent:
            self.current_session['intent'] = hard_code_intent

        await self.router.route()

    def send_to_user(self, msg):
        if self.current_session:
            msg = self.translator(dialogue=self.current_session['dialogue'], reply=msg).translated_reply
            self.ui.send(msg)
            wrapped_msg = self._wrap_msg(msg, 'Assistant')
            self._session_update(wrapped_msgs=[wrapped_msg])
        else:
            wrapped_msg = self._wrap_msg(msg, 'Assistant')
            self.start_new_session(first_wrapped_msg=wrapped_msg)
            self.ui.send(msg)



    async def send_wait_reply(self, msg) -> Dialogue:
        msg = self.translator(dialogue=self.current_session['dialogue'], reply=msg).translated_reply
        self.ui.send(msg)
        wrapped_msg = self._wrap_msg(msg, 'Assistant')
        reply = await self.ui.receive()
        wrapped_reply = self._wrap_msg(reply, 'User')

        self._session_update(wrapped_msgs=[wrapped_msg, wrapped_reply])
        return self.current_session['dialogue']

    async def send_wait_confirm(self, msg) -> tuple[Dialogue, bool]:
        dialogue = await self.send_wait_reply(msg)
        confirm = self.confirmor(dialogue=dialogue).confirmation
        return self.current_session['dialogue'], confirm


    async def wait_for_msg(self):
        while True:
            msg = await self.ui.receive()

            wrapped_msg = self._wrap_msg(msg, 'User')
            if self.current_session is None:
                self.start_new_session(first_wrapped_msg=wrapped_msg)
            else:
                self._session_update(wrapped_msgs=[wrapped_msg])
            await self.route()
    
    async def timely_task(self):
        while True:
            await asyncio.sleep(60)
            for reminder in self.reminders:
                if reminder.remind_date == dt.date.today() and reminder.remind_time == dt.datetime.now().time().replace(microsecond=0, second=0):
                    self.send_to_user(reminder.remind_content)
    
    
    async def run(self):
        """   
        Check time each second, each 60 second print current time
        """
        timely_task = asyncio.create_task(self.timely_task())
        wait_for_msg_task = asyncio.create_task(self.wait_for_msg())
        await asyncio.gather(timely_task, wait_for_msg_task)
