
from typing import Annotated, NamedTuple, Literal, Optional, Union

import dspy

from ..session import Dialogue

intents = ['Search', 'Chat']

class IntentRouterSig(dspy.Signature):
    f"""
    Classify user's latest intent by interpreting dialogue history. Current intents including {intents}
    If user is querying information which you don't exactly know, just classify it as 'Search'. If user is chatting with you, classify it as 'Chat'.
    Notice: schedule event is different with reminder. a event is reminded before it happens, so you need to distinguish them, give the intent of latest message from user.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    intent: Literal['Search', 'Chat'] = dspy.OutputField(desc=f"Intents including {intents}, pick one from list, without other redundant information")


