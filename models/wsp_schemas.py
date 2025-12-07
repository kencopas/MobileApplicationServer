from pydantic import BaseModel, Field
from typing import Dict, Optional


class WSPEvent(BaseModel):
    """A basic Websocket Protocol Event schema"""
    event: str = Field(description="The request event type")
    data: Optional[Dict] = Field(None, description="An optional request payload")
    error: Optional[str] = Field(None, description="Optional error message")
