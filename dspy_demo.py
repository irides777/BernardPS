
import dspy
import logging
import os
import asyncio
# import pandas as pd
# from openai import OpenAI
# from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from bernard.router import DialogueRouter
from bernard.server import ScheduleEventServer, GeneralChatServer
from bernard.channel import CMDInterface


router = DialogueRouter()
ui = CMDInterface(router)
router.add_server('Schedule Event', ScheduleEventServer(ui))
router.add_server('Chat', GeneralChatServer(ui))

lm = dspy.OpenAI(model='qwen-plus', api_base='https://dashscope.aliyuncs.com/compatible-mode/v1', api_key=os.getenv('DASHSCOPE_API_KEY'), model_type='chat')
dspy.settings.configure(lm=lm)

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    while True:
        asyncio.run(ui.wait_for_msg())