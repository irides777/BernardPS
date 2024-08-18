
import logging
from typing import Optional
import dspy
import re
import datetime as dt
from typing import Union, Literal

from ...session import Dialogue
from ...reply import ReplyInformationConfirmSig, ReplyQuerySig
from ..request import RequestServer
from .task import BaseTask, BaseProgress
from .datetime import relative_date_cal, process_raw_date
from .task_server import TaskNextRemindDateConstructorSig, TaskNextRemindTimeConstructorSig
class TaskMatchSig(dspy.Signature):
    """ 
    You are user's assistant, user has scheduled some long term tasks, you have recorded these tasks in list. Now user is talking about some task's progress, please extract the corresponding task in your list.
    """

    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time. User is now talking about some task's progress. You may find the task user mentioned at the beginning of dialogue.")
    task_list: list[str] = dspy.InputField(desc="List of tasks, the task you extract must be in this list.")
    task_user_mentioned_in_dialogue: str = dspy.OutputField(desc="The task corresponding to user mentioned in dialogue. If you can't find the appropriate task in task list, fill the field with 'unknown'. If you think there are multiple tasks in list matching the dialogue, fill the field with 'vague'. You return must be the same as any one in task list, DO NOT ADD '«»' ARUOUND RESULT, DO NOT RETURN TASK NOT IN TASK LIST, DO NOT ADD ANY EXPLANATION.")

class ProgressContentConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user has scheduled a task. Now user is talking about the task's progress, please extract the detail of progress user mentioned in dialogue. The return should be the same language as user's input. 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time.")
    task: str = dspy.InputField(desc="The task user is now talking about.")
    task_current_progress: str = dspy.OutputField(desc="Current progress of the task, summary from user's message in dialogue. Please be brief and clear. Do NOT add any explanation or title in the return. ")

class TaskPlanIfFinishedSig(dspy.Signature):
    """   
    You are user's assistant, user has scheduled a task, and planned a step to finish the task. Now user is talking about the task's current progress, please identify if the planned step is finished according to the user's progress.  
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    task: str = dspy.InputField(desc="The task user is now talking about.")
    step: str = dspy.InputField(desc="The current step of above task user planned some while ago.")
    if_step_finished: bool = dspy.OutputField(desc="Only True/False, indicating if the step user planned is finished according to the progress mentioned in dialogue. DO NOT ADD ANY EXPLANATION.")


class TaskNextStepConstructorSig(dspy.Signature):
    """   
    You are user's assistant, user has scheduled a task. To finish the task, user must take several steps. Now user have finished some steps, please extract the detail of next step user mentioned in dialogue. If user didn't mention next step, just fill the field with 'unknown'. The return should be the same language as user's input (except 'unknown'). 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    next_step: str = dspy.OutputField(desc="The next step user need to do to finish the task, be brief and clear, do not add any explanation or title. If user didn't mention next step of task, just fill the field with 'unknown'. DO NOT ADD ANY EXPLANATION.")


class ProgressLLM(dspy.Module):

    def __init__(self):
        super().__init__()
        self.task_matcher = dspy.TypedPredictor(TaskMatchSig)
        self.progress_content_constructor = dspy.TypedPredictor(ProgressContentConstructorSig)
        self.task_step_finished_identifier = dspy.TypedPredictor(TaskPlanIfFinishedSig)
        self.task_next_step_constructor = dspy.TypedPredictor(TaskNextStepConstructorSig)
        self.task_next_remind_date_constructor = dspy.TypedPredictor(TaskNextRemindDateConstructorSig)
        self.task_next_remind_time_constructor = dspy.TypedPredictor(TaskNextRemindTimeConstructorSig)
    
    def forward(self, dialogue: Dialogue, task_list: list[str] = [], step_map: dict[str, str] = {}):
        # reminder_reply = self.reminder_constructor(dialogue=dialogue)
        # print(reminder_reply)
        print(task_list)
        task_talked_about = self.task_matcher(dialogue=dialogue, task_list=task_list).task_user_mentioned_in_dialogue
        print(task_talked_about)

        raw_progress_content = self.progress_content_constructor(dialogue=dialogue, task=task_talked_about).task_current_progress
        progress_content = raw_progress_content.split('\n')[0]
        print(progress_content)

        print(step_map)

        step_planned = step_map.get(task_talked_about, 'unknown')
        print(step_planned)
        step_finished = self.task_step_finished_identifier(dialogue=dialogue, task=task_talked_about, step=step_planned).if_step_finished

        if step_finished:
            next_step = self.task_next_step_constructor(dialogue=dialogue).next_step
        else:
            next_step = step_planned

        
        raw_task_next_remind_date = self.task_next_remind_date_constructor(dialogue=dialogue).next_remind_date
        print(raw_task_next_remind_date)
        task_next_remind_date = process_raw_date(dialogue=dialogue, raw_date=raw_task_next_remind_date)

        task_next_remind_time = self.task_next_remind_time_constructor(dialogue=dialogue).next_remind_time
        print(task_next_remind_time)
        # reminder_time = raw_reminder_time if raw_reminder_time != 'unknown' else '12:00'

        print(f"task_remind_date: {task_next_remind_date}, task_remind_time: {task_next_remind_time}")
        progress = BaseProgress(
            task_current_progress=progress_content,
            last_step_finished=step_finished,
            current_step_of_task=next_step,
            next_remind_date=task_next_remind_date,
            next_remind_time=task_next_remind_time
        )

        # dspy.Suggest(
        #     self.reminder_checker(dialogue=dialogue, reminder=reminder).faithfulness,
        #     f"Reminder created {reminder} is not consistent with user mentioned in dialogue"
        # )
        return progress

# class TaskServer:
#     def __init__(self, channel):
#         self.name = 'Create Task'
#         self.channel = channel
#         self.reminder_creator = TaskLLM().activate_assertions(max_backtracks=1)
#         self.reply_confirm = dspy.TypedPredictor(ReplyInformationConfirmSig)
#         self.reply_query = dspy.TypedPredictor(ReplyQuerySig)

#     def add_task(self, task: BaseTask):
#         print(f'Task added: {task}')
#         # self.channel.tasks.append(reminder)
    
#     async def process_dialogue(self, dialogue: Dialogue):
#         task = self.task_creator(dialogue=dialogue)
#         unknown_fields = task.unknown_fields()
#         if len(unknown_fields) == 0:
#             self.add_task(task=task)
#             self.channel.send_to_user(f'task {task} created successfully!')
#             self.channel.end_current_session()
#         else:
#             reply_for_more_information = self.reply_query(dialogue=dialogue, incomplete_data=task).reply
#             self.channel.send_to_user(reply_for_more_information)

class ProgressServer(RequestServer):
    
    def __init__(self, channel):
        name = 'Create Task Update'
        super().__init__(name=name, channel=channel, RequestLLM=ProgressLLM)

    def add_request(self, progress: BaseProgress):
        print(f'progress added: {progress}')
        self.channel.step_map[progress.current_step_of_task] = progress.current_step_of_task