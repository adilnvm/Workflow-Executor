from pydantic import BaseModel
from typing import Optional, Dict, Any


class LLMResponse(BaseModel):
    content: str
    tool_call: Optional[Dict[str, Any]] = None
    confidence: float = 1.0
