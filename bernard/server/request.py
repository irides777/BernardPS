
from pydantic import BaseModel
import dspy
from ..reply import ReplyInformationConfirmSig, ReplyQuerySig
from ..session import Dialogue

class LLMRequest(BaseModel):

    def unknown_fields(self):
        ret = []
        for i in self:
            if i[1] == 'unknown':
                ret.append(i[0])
        return ret

class RequestServer:
    def __init__(self, name, channel, RequestLLM):
        self.name = name
        self.channel = channel
        self.request_creator = RequestLLM().activate_assertions(max_backtracks=1)
        self.reply_confirm = dspy.TypedPredictor(ReplyInformationConfirmSig)
        self.reply_query = dspy.TypedPredictor(ReplyQuerySig)

    def add_request(self, request):
        raise NotImplementedError()
    
    async def process_dialogue(self, dialogue: Dialogue):
        request = self.request_creator(dialogue=dialogue)
        unknown_fields = request.unknown_fields()
        if len(unknown_fields) == 0:
            # reply_for_confirmation = self.reply_confirm(dialogue=dialogue, information_need_check=reminder).reply
            # dialogue_after_confirm, confirm = await self.channel.send_wait_confirm(reply_for_confirmation)
            # if confirm:
            self.add_request(request=request)
            self.channel.send_to_user(f'{request} created successfully!')
            self.channel.end_current_session()
            # else:
            #     await self.channel.route(dialogue=dialogue_after_confirm)
        else:
            reply_for_more_information = self.reply_query(dialogue=dialogue, incomplete_data=request).reply
            self.channel.send_to_user(reply_for_more_information)
