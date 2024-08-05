import dspy
from ...session import Dialogue

class GeneralChatSig(dspy.Signature):
    """   
    You are user's assistant, when user is chatting with you without any specific intent, just chat with their like talking with friends. Please reply user in short and oral sentences, and follow user's language.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time. Notice that your reply shoule be in the same language as User's")
    reply: str = dspy.OutputField(desc="Just chat with user")