
from typing import Annotated, NamedTuple, Literal, Optional, Union

import dspy

from ..session import Dialogue

intents = ['Create Schedule Event', 'Create Time Reminder', 'Search', 'Chat']

class IntentRouterSig(dspy.Signature):
    f"""
    Classify user's latest intent by interpreting dialogue history. Current intents including {intents}
    Notice: schedule event is different with reminder. a event is reminded before it happens, so you need to distinguish them, give the intent of latest message from user.
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    intent: Literal['Create Schedule Event', 'Create Time Reminder', 'Search', 'Chat'] = dspy.OutputField(desc=f"Intents including {intents}, pick one from list, without other redundant information")


