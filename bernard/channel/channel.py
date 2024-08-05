
from typing import Literal
import datetime as dt
from ..session import SessionContext, Dialogue, Message, SessionEndDiscriminator

WEEKDAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

class CMDInterface:
    def __init__(self, router) -> None:
        self.workers = {}
        self.router = router
        self.session_end_disc = SessionEndDiscriminator()
        self.current_session = None
        self.history_sessions = []
    
    def _wrap_msg(self, msg, sender: Literal['User', 'Assistant']):
        return Message.model_validate({'role': sender, 'content': msg, 'date': dt.datetime.now().date(), 'time': dt.datetime.now().time().replace(microsecond=0), 'weekday': WEEKDAYS[dt.datetime.now().weekday()]})

    async def route(self, dialogue: Dialogue):
        if self.current_session:
            is_session_ended = self.session_end_disc.is_session_ended(dialogue)
        else:
            is_session_ended = False
        if is_session_ended:
            print('session ended!')
            self.history_sessions.append(self.current_session)
            dialogue.root = dialogue.root[-1:]
            self.current_session = SessionContext(dialogue=dialogue)
        await self.router.route(dialogue=dialogue)

    def send_to_user(self, msg):
        print('assistant:' + msg)
        wrapped_msg = self._wrap_msg(msg, 'Assistant')
        if not self.current_session:
            dialogue = Dialogue.model_validate([wrapped_msg])
            self.current_session = SessionContext(dialogue=dialogue)
        else:
            self.current_session.dialogue.root.extend([wrapped_msg])


    async def send_wait_reply(self, msg) -> Dialogue:
        print('assistant:' + msg)
        wrapped_msg = self._wrap_msg(msg, 'Assistant')
        reply = input('user:')
        wrapped_reply = self._wrap_msg(reply, 'User')

        if not self.current_session:
            dialogue = Dialogue.model_validate([wrapped_msg, wrapped_reply])
            self.current_session = SessionContext(dialogue=dialogue)
        else:
            self.current_session.dialogue.root.extend([wrapped_msg, wrapped_reply])
            dialogue = self.current_session.dialogue
        return dialogue

    async def wait_for_msg(self):
        msg = input('user:')

        wrapped_msg = self._wrap_msg(msg, 'User')
        if not self.current_session:
            dialogue = Dialogue.model_validate([wrapped_msg])
            self.current_session = SessionContext(dialogue=dialogue)
        else:
            self.current_session.dialogue.root.append(wrapped_msg)
            dialogue = self.current_session.dialogue
        await self.route(dialogue)