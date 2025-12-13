"""Memory Management Module."""

from .conversation_memory import ConversationMemory

# The __all__ variable defines the public interface of this module.
# It limits what is imported when using 'from memory import *' to just ConversationMemory.
# 
# 'ConversationMemory' is a class (defined in conversation_memory.py) that manages 
# the structured context, phase tracking, and message history for the OPT assistant. 
# It is responsible for storing and updating the user's business information and 
# tracking the flow of the conversation.
__all__ = ["ConversationMemory"]

