
import logging
from typing import Optional
import dspy
import re
import datetime as dt
from typing import Union, Literal

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from ..request import RequestServer
from .task import BaseTask
from .datetime import relative_date_cal, process_raw_date


class TaskContentConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is scheduling a task, with a specific deadline and next remind time. To finish the task, user must take several steps. Please extract the detail of task content and first step user mentioned in dialogue. If user didn't mention first step, just fill the field with 'unknown'. The return should be the same language as user's input (except 'unknown'). Distinguish the difference between task content and first step.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    task_content: str = dspy.OutputField(desc="The task content user want to set, be brief and clear, do not add any explanation or title. If user doesn't mention specific content, just fill it with 'task'. Notice: task_content is different from first step, first step is a part of how to finish the entire task.")
    first_step: str = dspy.OutputField(desc="The first step user need to do to finish the task, be brief and clear, do not add any explanation or title. If user didn't mention first step of task, just fill the field with 'unknown'. DO NOT ADD ANY EXPLANATION.")

class TaskDeadlineDateConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is scheduling a task, with a specific deadline and next remind time. please extract the deadline date of task user mentioned in dialogue. The return should be the same language as user's input (except 'unknown'). 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    deadline_date: Union[dt.date, str] = dspy.OutputField(desc="The deadline date of task user mentioned. Notice: if the date user mentioned is weekday related (e.g. next Wed, 这周五), you don't need to transform relative date into absolute date, just return exactly what user said. Otherwise, If user mentioned absolute date, return the date in format 'YYYY-MM-DD', with the current date information mentioned in dialogue. If there is insuffcient information to fill a field, just fill it with 'unknown'. DO NOT ADD ANY EXPLANATION.")
    next_remind_date: Union[dt.date, str] = dspy.OutputField(desc="The next remind date (TIME IS NOT REQUIRED) of task user mentioned. Caution: remind date is NOT the deadline date, if user only mentioned deadline date, please fill this field with 'unknown'. Notice: if the date user mentioned is weekday related (e.g. next Wed, 这周五), you don't need to transform relative date into absolute date, just return exactly what user said. Otherwise, If user mentioned absolute date, return the date in format 'YYYY-MM-DD', with the current date information mentioned in dialogue. If there is insuffcient information to fill a field, just fill it with 'unknown'. DO NOT ADD ANY EXPLANATION.")

# class TaskFirstStepConstructorSig(dspy.Signature):
#     """   
#     You are user's assistant, user is scheduling a task, with a specific deadline and next remind time. To finish the task, user must take the first step. Please extract the detail of first step user mentioned in dialogue. If user didn't mention first step, just fill the field with 'unknown'. The return should be the same language as user's input (except 'unknown'). 
#     """
#     dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
#     first_step: str = dspy.OutputField(desc="The first step user need to do to finish the task, be brief and clear, do not add any explanation or title. If user didn't mention first step of task, just fill the field with 'unknown'. DO NOT ADD ANY EXPLANATION.")

class TaskNextRemindDateConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is scheduling a task, with a specific deadline. You need to remind the task to user after a while. Please extract the next remind date of task user mentioned in dialogue. The return should be the same language as user's input (except 'unknown'). 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    next_remind_date: Union[dt.date, str] = dspy.OutputField(desc="The next remind date (TIME IS NOT REQUIRED) of task user mentioned. Caution: remind date is NOT the deadline date, if user only mentioned deadline date, please fill this field with 'unknown'. Notice: if the date user mentioned is weekday related (e.g. next Wed, 这周五), you don't need to transform relative date into absolute date, just return exactly what user said. Otherwise, If user mentioned absolute date, return the date in format 'YYYY-MM-DD', with the current date information mentioned in dialogue. If there is insuffcient information to fill a field, just fill it with 'unknown'. DO NOT ADD ANY EXPLANATION.")


class TaskNextRemindTimeConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user is scheduling a task, with a specific deadline. You need to remind the task to user after a while. Please extract the next remind time (date is not required) of task user mentioned in dialogue. The return should be the same language as user's input (except 'unknown'). 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    next_remind_time: Union[dt.time, Literal['unknown']] = dspy.OutputField(desc="The next remind time of task user want to set, not include date. (e.g. 10:00, 14:00, 17:30, etc.) If user doesn't mention specific time, just fill it with 'unknown'. ANY OUTPUT OTHER THAN 'unknown' DO NOT ADD ANY EXPLANATION.")

class TaskCheckerSig(dspy.Signature):
    """ 
    Verify that the auto generated task is based on the event user mentioned in provided dialogue. Especially check the datetime and weekday.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    task: BaseTask = dspy.InputField(desc="the task user mentioned")
    faithfulness: bool = dspy.OutputField(desc="ONLY output True or False indicating if task is faithful to dialogue, other redundant information should be ignored. Notice that task is different from schedule event.")


class TaskLLM(dspy.Module):

    def __init__(self):
        super().__init__()
        self.task_content_constructor = dspy.TypedPredictor(TaskContentConstructorSig, max_retries=3)
        self.task_deadline_date_constructor = dspy.TypedPredictor(TaskDeadlineDateConstructorSig)
        # self.task_first_step_constructor = dspy.TypedPredictor(TaskFirstStepConstructorSig)
        # self.task_next_remind_date_constructor = dspy.TypedPredictor(TaskNextRemindDateConstructorSig)
        self.task_next_remind_time_constructor = dspy.TypedPredictor(TaskNextRemindTimeConstructorSig)
        self.task_checker = dspy.TypedPredictor(TaskCheckerSig)
    
    def forward(self, dialogue: Dialogue):
        # reminder_reply = self.reminder_constructor(dialogue=dialogue)
        # print(reminder_reply)
        task_res = self.task_content_constructor(dialogue=dialogue)
        raw_task_content = task_res.task_content
        raw_first_step = task_res.first_step
        task_content = raw_task_content.split('\n')[0]
        first_step = raw_first_step.split('\n')[0]
        # print(task_content)

        # raw_first_step = self.task_first_step_constructor(dialogue=dialogue).first_step
        # print(first_step)


        # raw_task_deadline_date = self.task_deadline_date_constructor(dialogue=dialogue).deadline_date
        task_dates = self.task_deadline_date_constructor(dialogue=dialogue)
        raw_task_deadline_date = task_dates.deadline_date
        raw_task_next_remind_date = task_dates.next_remind_date
        # print(raw_task_deadline_date)
        # raw_task_next_remind_date = self.task_next_remind_date_constructor(dialogue=dialogue).next_remind_date
        # print(raw_task_next_remind_date)
        task_deadline_date = process_raw_date(dialogue=dialogue, raw_date=raw_task_deadline_date)
        task_next_remind_date = process_raw_date(dialogue=dialogue, raw_date=raw_task_next_remind_date)

        task_next_remind_time = self.task_next_remind_time_constructor(dialogue=dialogue).next_remind_time
        # print(task_next_remind_time)
        # reminder_time = raw_reminder_time if raw_reminder_time != 'unknown' else '12:00'

        print(f"deadline:{task_deadline_date} task_remind_date: {task_next_remind_date}, task_remind_time: {task_next_remind_time}")
        task = BaseTask(
            task_content=task_content,
            deadline_date=task_deadline_date,
            first_step=first_step,
            next_remind_date=task_next_remind_date,
            next_remind_time=task_next_remind_time
        )

        # dspy.Suggest(
        #     self.reminder_checker(dialogue=dialogue, reminder=reminder).faithfulness,
        #     f"Reminder created {reminder} is not consistent with user mentioned in dialogue"
        # )
        return task



class TaskServer(RequestServer):
    
    def __init__(self, channel):
        name = 'Create Task'
        super().__init__(name=name, channel=channel, RequestLLM=TaskLLM)

    def add_request(self, task: BaseTask):
        print(f'task added: {task}')
        self.channel.tasks.append(task.task_content)
        self.channel.step_map[task.task_content] = task.first_step