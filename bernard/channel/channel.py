
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

    def _session_update(self, wrapped_msgs: list[Message]):
        if not self.current_session:
            dialogue = Dialogue.model_validate(wrapped_msgs)
            self.current_session = SessionContext(dialogue=dialogue)
        else:
            self.current_session.dialogue.root.extend(wrapped_msgs)

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
        self._session_update(wrapped_msgs=[wrapped_msg])


    async def send_wait_reply(self, msg) -> Dialogue:
        print('assistant:' + msg)
        wrapped_msg = self._wrap_msg(msg, 'Assistant')
        reply = input('user:')
        wrapped_reply = self._wrap_msg(reply, 'User')

        self._session_update(wrapped_msgs=[wrapped_msg, wrapped_reply])
        return self.current_session.dialogue

    async def wait_for_msg(self):
        msg = input('user:')

        wrapped_msg = self._wrap_msg(msg, 'User')
        self._session_update(wrapped_msgs=[wrapped_msg])
        await self.route(dialogue)