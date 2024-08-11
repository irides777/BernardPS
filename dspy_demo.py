
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
from bernard.server import ScheduleEventServer, GeneralChatServer, ReminderServer
from bernard.channel import Channel
from bernard.ui import CmdUI


cmd_ui = CmdUI()
channel = Channel(ui=cmd_ui)
channel.router.add_server('Create Time Reminder', ReminderServer(channel))
channel.router.add_server('Chat', GeneralChatServer(channel))

lm = dspy.OpenAI(model='qwen-plus', api_base='https://dashscope.aliyuncs.com/compatible-mode/v1', api_key=os.getenv('DASHSCOPE_API_KEY'), model_type='chat')
dspy.settings.configure(lm=lm)

# class RelativeDateRetractSig(dspy.Signature):
#     """
#     You are user's assistant, user is setting some schedule in previous dilogue, please extract the detail of date user mentioned in message, fill the relevant information to construct a date for storing into database. If user have not mentioned information about relative date, just fill it with 'unknown'.
#     """
#     dialogue: dspy.Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
#     relative_date: dspy.Date = dspy.OutputField(desc="the relative date user want to set. If there is insuffcient information to fill a field, just fill it with 'unknown'.")


if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    # teleprompter = BootstrapFewShot(metric=validate_answer)
    # optimized_program = teleprompter.compile(pred, trainset=trainset)
    # optimized_program.save('model.json')
    # print(optimized_program(current_weekday='Sat', relative_weekday_or_date='下下周五').date_delta)
    asyncio.run(channel.run())