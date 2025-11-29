from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ActionLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    action: str
    entity: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class ActionLogListResponse(BaseModel):
    items: List[ActionLogResponse]
    total: int
    page: int
    size: int
    pages: int


class ActionLogFilter(BaseModel):
    action: Optional[str] = None
    entity: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
