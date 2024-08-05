import dspy

from ..session import Dialogue

class SessionEndSig(dspy.Signature):
    """  
    You are user's assistant, please analysis dialogue, and judge if user want to end the current topic in previous dialogue. Both user want to talk about another topic, and want to end the chat, all indicate the end of session, return True. Otherwise (i.e. still talk about current topic) return False. 
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time.")
    is_session_ended: bool = dspy.OutputField(desc="True/False indicating if current session is ended by user.")