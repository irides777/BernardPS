import dspy
from pydantic import BaseModel

from ..session import Dialogue

class ReplyActionConfirmationSig(dspy.Signature):
    """
    You are user's assistant, you are going to take some action, please design a reply to asking user for confirmation, use short and oral sentences, follow user's language.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time. Notice that your reply shoule be in the same language as User's")
    action: str = dspy.InputField(desc="The action you are going to take, please retrieve the action and put into your reply")
    reply: str = dspy.OutputField(desc="The reply you designed to ask user for confirmation, your reply should be short and clear, and be consistent with user in LANGUAGE")

class ReplyQuerySig(dspy.Signature):
    """
    You are user's assistant, please based on dialogue and incomplete data, design a reply to asking user for the information needed to complete data, use short and oral sentences, follow user's language.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time. Notice that your reply shoule be in the same language as User's")
    incomplete_data: BaseModel = dspy.InputField(desc="The incomplete data, the value unknown fields are 'unknown'. Unknown fields are not mentioned or not clear in dialogue, need to ask user for reply")
    reply: str = dspy.OutputField(desc="The reply you designed to query user for completing data, your reply should be short and clear, and be consistent with user in LANGUAGE")

class ReplyInformationConfirmSig(dspy.Signature):
    """
    You are user's assistant, there is some information need user's check and confirmation, please design a reply to asking user for their confirmation to the information, use short and oral sentences, follow user's language.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time. Notice that your reply shoule be in the same language as User's")
    information_need_check: BaseModel = dspy.InputField(desc="The information which need user's check and confirmation, please retrieve the information and put into your reply")
    reply: str = dspy.OutputField(desc="The reply you designed to send to user for confirmation to information_need_check, not information in dialogue, your reply should be short and clear, and be consistent with user in LANGUAGE")