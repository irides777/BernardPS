import dspy

from ..session import Dialogue

class GeneralConfirmationSig(dspy.Signature):
    """  
    check if user's last reply has confirmed the assistant's query, or mentioned any revise
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    confirmation: bool = dspy.OutputField(desc="True/False indicating if user's last reply confirm the assistant's query. Any revise or termination mentioned should return False")

class LanguageTranslatorSig(dspy.Signature):
    """  
    Translate the reply from auto generated to user's language. If the reply is the same as user's, just return the original reply.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    reply: str = dspy.InputField(desc="The reply from auto generated")
    translated_reply: str = dspy.OutputField(desc="The reply translated to user's language. If the reply is the same as user's, just return the original reply, DON'T ADD ANYTHING RATHER THAN ORIGINAL REPLY.")