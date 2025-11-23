from pydantic import BaseModel, Field
from typing import Dict, Optional


class WSPEvent(BaseModel):
    """A basic Websocket Protocol Event schema"""
    event: str = Field(description="The request event type")
    data: Optional[Dict] = Field(description="An optional request payload")
    request_id: Optional[str] = Field(None, alias="requestId", description="Optional request ID")
