
from typing import Annotated, NamedTuple, Literal, Optional, Union

import dspy

from ..session import Dialogue


class IntentRouterSig(dspy.Signature):
    """
    Classify user's intent by interpreting dialogue history. Current intents including [schedule event, search, chat]
    """
    dialogue: Dialogue = dspy.InputField(desc="Dialogue consists of role, content and time")
    intent: Literal['Schedule Event', 'Search', 'Chat'] = dspy.OutputField(desc="Intents including [Schedule Event, Search, Chat], pick one from list, without other redundant information")


