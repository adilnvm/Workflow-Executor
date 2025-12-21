from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    message: str
    ticket_id: Optional[str] = None
