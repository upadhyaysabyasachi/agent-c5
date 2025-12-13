"""OPT Framework Prompts Module."""

from .opt_coach import (
    DISCOVERY_SYSTEM_PROMPT,
    ANALYSIS_SYSTEM_PROMPT,
    CODE_GEN_SYSTEM_PROMPT,
)
from .task_analysis import TASK_ANALYSIS_PROMPT
from .code_generation import CODE_GENERATION_PROMPT

__all__ = [
    "DISCOVERY_SYSTEM_PROMPT",
    "ANALYSIS_SYSTEM_PROMPT",
    "CODE_GEN_SYSTEM_PROMPT",
    "TASK_ANALYSIS_PROMPT",
    "CODE_GENERATION_PROMPT",
]

