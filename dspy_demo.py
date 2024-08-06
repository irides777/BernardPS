
import dspy
import logging
import os
import asyncio
# import pandas as pd
# from openai import OpenAI
# from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from bernard.router import DialogueRouter
from bernard.server import ScheduleEventServer, GeneralChatServer, ReminderServer
from bernard.channel import Channel
from bernard.ui import CmdUI


router = DialogueRouter()
cmd_ui = CmdUI()
channel = Channel(router=router, ui=cmd_ui)
router.add_server('Create Schedule Event', ScheduleEventServer(channel))
router.add_server('Create Time Reminder', ReminderServer(channel))
router.add_server('Chat', GeneralChatServer(channel))

lm = dspy.OpenAI(model='qwen-plus', api_base='https://dashscope.aliyuncs.com/compatible-mode/v1', api_key=os.getenv('DASHSCOPE_API_KEY'), model_type='chat')
dspy.settings.configure(lm=lm)

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    while True:
        asyncio.run(channel.wait_for_msg())