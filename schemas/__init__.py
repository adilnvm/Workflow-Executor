from .decision import Decision
from pydantic import BaseModel
from typing import Any, Optional, Dict

class LLMResponse(BaseModel):
    content: str
    confidence: float
    tool_call: Optional[Dict[str, Any]] = None
