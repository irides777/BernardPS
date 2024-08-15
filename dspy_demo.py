
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
from bernard.server import ScheduleEventServer, GeneralChatServer, ReminderServer, TaskServer
from bernard.channel import Channel
from bernard.ui import CmdUI, WxautoUI

from wxauto import WeChat

from dotenv import load_dotenv, find_dotenv

# 一、自动搜索 .env 文件
load_dotenv(verbose=True)


# cmd_ui = CmdUI()
wx = WeChat()
wx_ui = WxautoUI(wx_window=wx, user_name='irides')
channel = Channel(ui=wx_ui)
channel.router.add_server('Create Time Reminder', ReminderServer(channel))
channel.router.add_server('Create Task', TaskServer(channel))
channel.router.add_server('Chat', GeneralChatServer(channel))

wx_ui2 = WxautoUI(wx_window=wx, user_name='123')
channel2 = Channel(ui=wx_ui2)
channel2.router.add_server('Create Time Reminder', ReminderServer(channel2))
channel2.router.add_server('Chat', GeneralChatServer(channel2))

lm = dspy.OpenAI(model='qwen-plus', api_base='https://dashscope.aliyuncs.com/compatible-mode/v1', api_key=os.getenv('DASHSCOPE_API_KEY'), model_type='chat')
dspy.settings.configure(lm=lm)

# class RelativeDateRetractSig(dspy.Signature):
#     """
#     You are user's assistant, user is setting some schedule in previous dilogue, please extract the detail of date user mentioned in message, fill the relevant information to construct a date for storing into database. If user have not mentioned information about relative date, just fill it with 'unknown'.
#     """
#     dialogue: dspy.Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
#     relative_date: dspy.Date = dspy.OutputField(desc="the relative date user want to set. If there is insuffcient information to fill a field, just fill it with 'unknown'.")

async def main():
    task1 = asyncio.create_task(channel.run())
    task2 = asyncio.create_task(channel2.run())
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    asyncio.run(main())
    # teleprompter = BootstrapFewShot(metric=validate_answer)
    # optimized_program = teleprompter.compile(pred, trainset=trainset)
    # optimized_program.save('model.json')
    # print(optimized_program(current_weekday='Sat', relative_weekday_or_date='下下周五').date_delta)
