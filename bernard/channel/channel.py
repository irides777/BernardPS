
import dspy
from typing import Literal
import datetime as dt
from ..session import SessionContext, Dialogue, Message, SessionEndDiscriminator
from .channel_llm import GeneralConfirmationSig, LanguageTranslatorSig

WEEKDAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

class Channel:
    def __init__(self, router, ui) -> None:
        self.workers = {}
        self.router = router
        self.session_end_disc = SessionEndDiscriminator()
        self.confirmor = dspy.TypedPredictor(GeneralConfirmationSig)
        self.translator = dspy.TypedPredictor(LanguageTranslatorSig)
        self.current_session = None
        self.history_sessions = []
        self.ui = ui
    
    def _wrap_msg(self, msg, sender: Literal['User', 'Assistant']):
        return Message.model_validate({'role': sender, 'content': msg, 'date': dt.datetime.now().date(), 'time': dt.datetime.now().time().replace(microsecond=0), 'weekday': WEEKDAYS[dt.datetime.now().weekday()]})

    def _session_update(self, wrapped_msgs: list[Message]):
        if not self.current_session:
            dialogue = Dialogue.model_validate(wrapped_msgs)
            self.current_session = SessionContext(dialogue=dialogue)
        else:
            self.current_session['dialogue'].root.extend(wrapped_msgs)

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
        msg = self.translator(dialogue=self.current_session['dialogue'], reply=msg).translated_reply
        self.ui.send(msg)
        wrapped_msg = self._wrap_msg(msg, 'Assistant')
        self._session_update(wrapped_msgs=[wrapped_msg])


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
        msg = await self.ui.receive()

        wrapped_msg = self._wrap_msg(msg, 'User')
        self._session_update(wrapped_msgs=[wrapped_msg])
        await self.route(self.current_session['dialogue'])