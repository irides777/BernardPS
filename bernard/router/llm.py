
from typing import Annotated, NamedTuple, Literal, Optional, Union

import dspy

from ..session import Dialogue

intents = ['Create Schedule Event', 'Create Time Reminder' 'Search', 'Chat']

class IntentRouterSig(dspy.Signature):
    f"""
    Classify user's latest intent by interpreting dialogue history. Current intents including {intents}
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    intent: Literal['Create Schedule Event', 'Create Time Reminder' 'Search', 'Chat'] = dspy.OutputField(desc=f"Intents including {intents}, pick one from list, without other redundant information")


