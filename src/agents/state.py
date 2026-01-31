from typing import Annotated, List, TypedDict, Union
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # The list of messages in the conversation
    messages: Annotated[List[BaseMessage], operator.add]
    # The current step/thought of the agent
    current_step: str
    # Context retrieved from the RAG layer
    context: List[str]
    # Whether the agent is ready to respond to the user
    is_complete: bool
    # Financial data or session specific parameters
    session_data: dict
