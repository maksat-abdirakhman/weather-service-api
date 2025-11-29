from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.log import ActionLogResponse, ActionLogListResponse
from app.services.log_service import LogService
import math

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/", response_model=ActionLogListResponse)
async def get_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = LogService(db)
    items, total = await service.get_logs(
        page=page,
        size=size,
        action=action,
        entity=entity,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    
    pages = math.ceil(total / size) if total > 0 else 1
    
    return ActionLogListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/summary")
async def get_logs_summary(db: AsyncSession = Depends(get_db)):
    service = LogService(db)
    return await service.get_actions_summary()


@router.get("/{log_id}", response_model=ActionLogResponse)
async def get_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = LogService(db)
    log = await service.get_log_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return log
