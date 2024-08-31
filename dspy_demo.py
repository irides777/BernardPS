
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy.evaluate.metrics import answer_exact_match
import logging
import os
import asyncio
# import pandas as pd
# from openai import OpenAI
# from pydantic import BaseModel, RootModel, Field, model_serializer, field_validator, ValidationInfo

from bernard.router import DialogueRouter
from bernard.server import GeneralChatServer, ReminderServer, TaskServer, ProgressServer
from bernard.channel import Channel
from bernard.ui import CmdUI, WxautoUI

from wxauto import WeChat

from dotenv import load_dotenv, find_dotenv

# 一、自动搜索 .env 文件
load_dotenv(verbose=True)


# cmd_ui = CmdUI()
wx = WeChat()
wx_ui = WxautoUI(wx_window=wx, user_name='')
channel = Channel(ui=cmd_ui)
channel.router.add_server('Create Time Reminder', ReminderServer(channel))
channel.router.add_server('Create Task', TaskServer(channel))
channel.router.add_server('Update Task Progress', ProgressServer(channel))
channel.router.add_server('Chat', GeneralChatServer(channel))



lm = dspy.OpenAI(model='qwen-max', api_base='https://dashscope.aliyuncs.com/compatible-mode/v1', api_key=os.getenv('DASHSCOPE_API_KEY'), model_type='chat')
dspy.settings.configure(lm=lm)


async def main():
    task1 = asyncio.create_task(channel.run())
    await asyncio.gather(task1)


if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    asyncio.run(main())
